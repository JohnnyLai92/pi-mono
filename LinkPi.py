#!/usr/bin/env python3
"""
LinkPi.py  –  OpenAI-compatible HTTP bridge for pi-mono
with per-provider sessions and cross-provider memory consolidation
=================================================================

Architecture
------------
  OpenCode (VS Code extension)
    │  POST /v1/chat/completions  (OpenAI streaming API)
    │  model: "link-pi/<provider>"  ← provider encoded in model name
    ▼
  LinkPi.py  (FastAPI HTTP server)
    │
    ├── ProviderRegistry
    │     one PiProcess per provider, each with its own session directory
    │     detects provider switch → compact outgoing session → update SharedMemory
    │
    ├── SharedMemory  (~/.linkpi/memory.md)
    │     cross-provider context injected at the start of every new session
    │     built from compact summaries of all prior provider sessions
    │
    └── /v1/consolidate
          spawns a fresh pi session, feeds it all provider summaries,
          asks it to produce one unified memory document
    │
    ▼  JSONL over stdin/stdout  (pi RPC protocol)
  pi --mode rpc  (one subprocess per provider)
    │  --session-dir ~/.linkpi/sessions/<provider>/
    ▼
  LLM provider  (Anthropic / OpenAI / Google / …)

Model naming in opencode.json
------------------------------
  OpenCode only accepts baseURL/apiKey inside *built-in* provider names.
  Use the built-in "openai" provider pointing at LinkPi, then select
  a model from the pi-* namespace:

    "model": "openai/pi-anthropic"   →  pi --provider anthropic
    "model": "openai/pi-openai"      →  pi --provider openai
    "model": "openai/pi-google"      →  pi --provider google
    "model": "openai/pi-agent"       →  pi (no provider override)

  Switch model in OpenCode's model selector (Ctrl+M) to switch providers.
  LinkPi will automatically compact the outgoing session and carry
  the memory forward to the new provider.

Memory flow
-----------
  Provider A active  →  user switches to Provider B in OpenCode
    1. LinkPi requests compact on Provider A's pi session
    2. Pi returns a handoff summary (plain text)
    3. Summary appended to ~/.linkpi/memory.md
    4. Provider B's pi session starts; shared memory is prepended
       to the first user message as a [Context] block
    5. Provider B continues work with full awareness of what A did

  POST /v1/consolidate
    Spawns a temporary pi session, feeds it ALL provider summaries,
    and asks it to synthesise a single unified memory document that
    replaces memory.md.

Endpoints
---------
  GET  /v1/models       – list available link-pi/<provider> models
  POST /v1/chat/completions – chat with streaming (OpenAI-compatible)
  POST /v1/consolidate  – synthesise all summaries into unified memory
  GET  /v1/memory       – inspect current shared memory

Usage
-----
  pip install fastapi uvicorn
  python LinkPi.py
  python LinkPi.py --model anthropic/claude-sonnet-4 --thinking medium
  python LinkPi.py --pi-cmd /path/to/pi-dev.sh --port 9000

RPC note
--------
  pi RPC command responses are routed via asyncio.Future (keyed by id)
  rather than through the event queue.  This allows send_command() to
  await a response synchronously while the event queue continues to
  receive streaming events from concurrent operations.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import shutil
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator, Optional

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

# ─── Logging ─────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
)
log = logging.getLogger("linkpi")

# ─── Constants ───────────────────────────────────────────────────────────────

LINKPI_DIR          = Path(os.environ.get("LINKPI_DIR", Path.home() / ".linkpi"))
SESSION_IDLE_TIMEOUT = 1800   # seconds; idle non-active providers are reaped
EVENT_READ_TIMEOUT   = 120    # seconds; max wait for next streaming event
COMPACT_TIMEOUT      = 300    # seconds; max wait for compact command response

# Map from model ID (as sent by OpenCode) to pi --provider value.
# OpenCode may prefix model IDs with "openai/" – _parse_provider strips that.
MODEL_TO_PROVIDER: dict[str, str] = {
    "pi-anthropic":  "anthropic",
    "pi-openai":     "openai",
    "pi-google":     "google",
    "pi-groq":       "groq",
    "pi-mistral":    "mistral",
    "pi-bedrock":    "bedrock",
    "pi-vertex":     "vertex",
    "pi-openrouter": "openrouter",
    "pi-local":      "local-llm",  # local vLLM/Ollama (models.json)
    "pi-agent":      "pi-agent",   # pi chooses provider
}


# ─── SharedMemory ─────────────────────────────────────────────────────────────

class SharedMemory:
    """
    Persists cross-provider handoff summaries as markdown files.

    Directory layout:
      ~/.linkpi/
        memory.md               ← active shared context (injected into new sessions)
        summaries/
          <provider>-<ts>.md    ← individual compact snapshots, one per switch
    """

    def __init__(self, base: Path = LINKPI_DIR) -> None:
        self._base          = base
        self._memory_file   = base / "memory.md"
        self._summaries_dir = base / "summaries"
        self._base.mkdir(parents=True, exist_ok=True)
        self._summaries_dir.mkdir(exist_ok=True)

    def get(self) -> str:
        """Return current shared memory, or '' if none exists yet."""
        return self._memory_file.read_text("utf-8").strip() \
               if self._memory_file.exists() else ""

    def set(self, content: str) -> None:
        self._memory_file.write_text(content, "utf-8")
        log.info("SharedMemory updated  chars=%d", len(content))

    def add_provider_summary(self, provider: str, summary: str) -> None:
        """
        Append *summary* (from a compact command) to memory.md and save
        a dated snapshot under summaries/.
        """
        if not summary.strip():
            return
        ts   = datetime.now().strftime("%Y%m%d-%H%M%S")
        snap = self._summaries_dir / f"{provider}-{ts}.md"
        snap.write_text(summary, "utf-8")

        existing = self.get()
        section  = f"\n\n## [{provider}]  {ts}\n\n{summary.strip()}"
        self.set((existing + section).strip())
        log.info("Added summary  provider=%s  chars=%d", provider, len(summary))

    def get_all_snapshots(self) -> list[tuple[str, str]]:
        """Return [(provider, content), …] sorted by filename (chronological)."""
        out = []
        for f in sorted(self._summaries_dir.glob("*.md")):
            # filename: "<provider>-YYYYMMDD-HHMMSS.md"
            provider = "-".join(f.stem.split("-")[:-2]) or f.stem
            out.append((provider, f.read_text("utf-8")))
        return out


# ─── PiProcess ───────────────────────────────────────────────────────────────

class PiProcess:
    """
    One pi --mode rpc subprocess.

    stdout reader splits output into two lanes:
      • event_queue   – agent events (message_update, agent_end, …)
      • _pending      – command responses, keyed by id, resolved via Future

    This lets send_command() await a response synchronously while the
    caller independently drains event_queue for streaming output.
    """

    def __init__(
        self,
        provider: str,
        process:  asyncio.subprocess.Process,
    ) -> None:
        self.provider:           str                      = provider
        self.process:            asyncio.subprocess.Process = process
        self.event_queue:        asyncio.Queue            = asyncio.Queue()
        self.user_message_count: int                      = 0
        self.last_used:          float                    = time.time()
        self.lock:               asyncio.Lock             = asyncio.Lock()
        self._pending:           dict[str, asyncio.Future] = {}
        self._reader_task:       asyncio.Task             = asyncio.create_task(
            self._read_loop()
        )

    # ── factory ──────────────────────────────────────────────────────────────

    @classmethod
    async def spawn(cls, provider: str, cmd: list[str]) -> "PiProcess":
        log.info("Spawn  provider=%-12s  cmd=%s", provider, " ".join(cmd))
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except (FileNotFoundError, PermissionError) as exc:
            raise RuntimeError(
                f"Cannot start pi: {exc}\n"
                f"  command tried: {cmd[0]}\n"
                f"  tip: use --pi-cmd to specify the full path, e.g. --pi-cmd pi.cmd (Windows)"
            ) from exc
        return cls(provider, proc)

    # ── reader ───────────────────────────────────────────────────────────────

    async def _read_loop(self) -> None:
        assert self.process.stdout
        buf = b""
        try:
            while True:
                chunk = await self.process.stdout.read(8192)
                if not chunk:
                    break
                buf += chunk
                while b"\n" in buf:
                    raw, buf = buf.split(b"\n", 1)
                    raw = raw.rstrip(b"\r")
                    if not raw:
                        continue
                    try:
                        msg = json.loads(raw.decode("utf-8", errors="replace"))
                    except json.JSONDecodeError:
                        continue

                    # Command responses (have matching id) → resolve Future
                    if msg.get("type") == "response" and "id" in msg:
                        fut = self._pending.get(msg["id"])
                        if fut and not fut.done():
                            fut.set_result(msg)
                        continue   # do NOT also push to event_queue

                    # Everything else (events) → event_queue
                    await self.event_queue.put(msg)

        except Exception as exc:
            log.error("reader crashed  provider=%s  %s", self.provider, exc)
        finally:
            await self.event_queue.put(None)   # sentinel

    # ── command helper ────────────────────────────────────────────────────────

    async def send_command(self, cmd: dict, timeout: float = 30.0) -> dict:
        """
        Send *cmd* to pi stdin and await the correlated response by id.
        Raises TimeoutError if no response arrives within *timeout* seconds.
        """
        cid       = uuid.uuid4().hex
        cmd       = {**cmd, "id": cid}
        loop      = asyncio.get_running_loop()
        fut: asyncio.Future = loop.create_future()
        self._pending[cid]  = fut

        assert self.process.stdin
        self.process.stdin.write((json.dumps(cmd) + "\n").encode())
        await self.process.stdin.drain()

        try:
            return await asyncio.wait_for(asyncio.shield(fut), timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"Command '{cmd.get('type')}' timed out after {timeout}s"
            )
        finally:
            self._pending.pop(cid, None)

    # ── memory compaction ─────────────────────────────────────────────────────

    async def compact_for_memory(self) -> str:
        """
        Request a compact on this session and return the summary text.
        The summary is suitable for handoff to another AI provider.
        Returns '' on failure or if the session is too short to compact.
        """
        instructions = (
            "Create a concise handoff summary for another AI assistant "
            "that will continue this work.  Cover: "
            "(1) project context and goals, "
            "(2) key decisions and their rationale, "
            "(3) code and architectural changes made, "
            "(4) current state and the most important next steps.  "
            "Be specific and actionable."
        )
        try:
            resp = await self.send_command(
                {"type": "compact", "customInstructions": instructions},
                timeout=COMPACT_TIMEOUT,
            )
            if resp.get("success"):
                return resp.get("data", {}).get("summary", "")
            log.warning(
                "compact failed  provider=%s  error=%s",
                self.provider, resp.get("error"),
            )
        except Exception as exc:
            log.warning("compact_for_memory error  provider=%s  %s", self.provider, exc)
        return ""

    # ── lifecycle ─────────────────────────────────────────────────────────────

    async def terminate(self) -> None:
        self._reader_task.cancel()
        try:
            self.process.terminate()
            await asyncio.wait_for(self.process.wait(), timeout=5)
        except Exception:
            self.process.kill()
        log.info("Terminated  provider=%s", self.provider)


# ─── Platform helpers ───────────────────────────────────────────────────────

def _resolve_cmd(pi_cmd: str) -> str:
    """
    On Windows, npm global scripts are .cmd wrappers.  Python's
    asyncio.create_subprocess_exec uses CreateProcess directly and cannot
    execute .cmd files without going through cmd.exe, but shutil.which()
    honours PATHEXT and returns the full .cmd path which CreateProcess
    accepts on modern Windows (8+).

    Falls back to the original string if resolution fails so the user
    gets a clear FileNotFoundError rather than a silent hang.
    """
    resolved = shutil.which(pi_cmd)
    if resolved:
        return resolved
    if sys.platform == "win32":
        resolved = shutil.which(pi_cmd + ".cmd")
        if resolved:
            return resolved
    return pi_cmd   # let spawn() raise FileNotFoundError with a clear message


# ─── ProviderRegistry ─────────────────────────────────────────────────────────

class ProviderRegistry:
    """
    Owns one PiProcess per provider.

    When the active provider changes (detected by comparing the model field
    across requests), the outgoing session is compacted and its summary is
    appended to SharedMemory before the incoming session is started.
    """

    def __init__(
        self,
        pi_cmd:  str,
        pi_extra: list[str],
        memory:  SharedMemory,
    ) -> None:
        self._pi_cmd   = pi_cmd
        self._pi_extra = pi_extra
        self.memory    = memory
        self._procs:   dict[str, PiProcess]   = {}
        self._active:  Optional[str]          = None
        self._sw_lock: asyncio.Lock           = asyncio.Lock()
        self._gc_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        self._gc_task = asyncio.create_task(self._gc_loop())
        log.info("ProviderRegistry ready  memory=%s", self.memory._memory_file)

    async def stop(self) -> None:
        if self._gc_task:
            self._gc_task.cancel()
        for p in list(self._procs.values()):
            await p.terminate()

    async def get(self, provider: str) -> PiProcess:
        """
        Return the PiProcess for *provider*.
        If *provider* differs from the currently active one, compact the
        outgoing session and update shared memory first.
        """
        async with self._sw_lock:
            if self._active and self._active != provider:
                await self._handle_switch(self._active, provider)

            if provider not in self._procs:
                self._procs[provider] = await self._spawn(provider)

            self._active            = provider
            self._procs[provider].last_used = time.time()
            return self._procs[provider]

    # ── internals ────────────────────────────────────────────────────────────

    async def _spawn(self, provider: str) -> PiProcess:
        session_dir = LINKPI_DIR / "sessions" / provider
        session_dir.mkdir(parents=True, exist_ok=True)

        cmd = [_resolve_cmd(self._pi_cmd), "--mode", "rpc", "--session-dir", str(session_dir)]
        if provider != "pi-agent":
            cmd += ["--provider", provider]
        cmd += self._pi_extra

        return await PiProcess.spawn(provider, cmd)

    async def _handle_switch(self, from_p: str, to_p: str) -> None:
        """
        Compact the outgoing provider's session and update SharedMemory.
        Called while _sw_lock is held, so the switch is atomic.
        """
        log.info("Provider switch  %s → %s", from_p, to_p)
        old = self._procs.get(from_p)
        if old and old.user_message_count > 0:
            log.info("Compacting outgoing session  provider=%s …", from_p)
            summary = await old.compact_for_memory()
            if summary:
                self.memory.add_provider_summary(from_p, summary)
            else:
                log.info("No summary produced (session may be too short)")

    async def _gc_loop(self) -> None:
        """Reap idle non-active sessions."""
        while True:
            await asyncio.sleep(60)
            now   = time.time()
            stale = [
                p for p in list(self._procs.values())
                if p.provider != self._active
                and now - p.last_used > SESSION_IDLE_TIMEOUT
            ]
            for p in stale:
                log.info("GC  provider=%s", p.provider)
                self._procs.pop(p.provider, None)
                await p.terminate()


# ─── Conversation-history helpers ─────────────────────────────────────────────

def _text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(
            b.get("text", "")
            for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        )
    return str(content)


def _last_user_text(messages: list[dict]) -> str:
    for m in reversed(messages):
        if m.get("role") == "user":
            return _text(m.get("content", ""))
    return ""


def _history_block(messages: list[dict]) -> str:
    """Format all messages before the last user turn as a readable block."""
    prior: list[dict] = []
    found = False
    for m in reversed(messages):
        if not found and m.get("role") == "user":
            found = True
            continue
        prior.append(m)
    prior.reverse()
    if not prior:
        return ""
    lines = ["[Previous conversation]"]
    for m in prior:
        lines.append(f"{m.get('role','?').capitalize()}: {_text(m.get('content',''))}")
    lines.append("[End previous conversation]")
    return "\n".join(lines)


def _tool_label(name: str, args: dict) -> str:
    if name == "bash":
        return f"bash `{args.get('command','')[:60].replace(chr(10),' ')}`"
    if name in ("read", "write", "edit"):
        return f"{name} {args.get('path', args.get('file_path',''))}"
    return name


# ─── OpenAI SSE helpers ───────────────────────────────────────────────────────

def _sse(text: str, cid: str, finish: Optional[str] = None) -> str:
    payload = {
        "id":      f"chatcmpl-{cid}",
        "object":  "chat.completion.chunk",
        "created": int(time.time()),
        "model":   "pi-agent",
        "choices": [{
            "index":         0,
            "delta":         {"content": text} if (text and not finish) else {},
            "finish_reason": finish,
        }],
    }
    return f"data: {json.dumps(payload)}\n\n"


# ─── Core streaming generator ─────────────────────────────────────────────────

async def _stream_prompt(
    proc:   PiProcess,
    prompt: str,
    cid:    str,
) -> AsyncIterator[str]:
    """
    Send *prompt* to pi and yield OpenAI SSE chunks until agent_end.
    Must be called while proc.lock is held.
    """
    # Send the prompt; the ack response is routed to a Future via send_command,
    # not to the event_queue, so it won't interfere with streaming.
    await proc.send_command({"type": "prompt", "message": prompt}, timeout=15)
    proc.user_message_count += 1
    log.info(
        "Prompt sent  provider=%-12s  turn=%d  len=%d",
        proc.provider, proc.user_message_count, len(prompt),
    )

    try:
        while True:
            try:
                event: Optional[dict] = await asyncio.wait_for(
                    proc.event_queue.get(), timeout=EVENT_READ_TIMEOUT
                )
            except asyncio.TimeoutError:
                yield _sse("\n\n*[LinkPi: timeout waiting for pi]*", cid)
                break

            if event is None:
                log.warning("Pi process ended  provider=%s", proc.provider)
                break

            et = event.get("type", "")

            if et == "message_update":
                ae = event.get("assistantMessageEvent", {})
                if ae.get("type") == "text_delta" and (delta := ae.get("delta", "")):
                    yield _sse(delta, cid)

            elif et == "tool_execution_start":
                label = _tool_label(event.get("toolName", "?"), event.get("args", {}))
                yield _sse(f"\n\n*[▶ {label}]*\n", cid)

            elif et == "tool_execution_end":
                name   = event.get("toolName", "?")
                mark   = "✗" if event.get("isError") else "✓"
                yield _sse(f"*[{mark} {name}]*\n\n", cid)

            elif et == "agent_end":
                log.info("Agent done  provider=%s", proc.provider)
                break

            elif et == "compaction_end":
                log.info("Context compacted  provider=%s", proc.provider)

            elif et == "auto_retry_start":
                yield _sse(f"\n*[retry {event.get('attempt')}…]*\n", cid)

    except Exception as exc:
        log.exception("Stream error  provider=%s", proc.provider)
        yield _sse(f"\n\n*[LinkPi error: {exc}]*", cid)

    yield _sse("", cid, finish="stop")
    yield "data: [DONE]\n\n"


def _locked_stream(proc: PiProcess, prompt: str, cid: str) -> AsyncIterator[str]:
    """Wrap _stream_prompt so proc.lock is held for the whole round-trip."""
    async def _gen() -> AsyncIterator[str]:
        async with proc.lock:
            async for chunk in _stream_prompt(proc, prompt, cid):
                yield chunk
    return _gen()


# ─── Memory consolidation ─────────────────────────────────────────────────────

async def _consolidate(
    pi_cmd:  str,
    pi_extra: list[str],
    memory:  SharedMemory,
) -> str:
    """
    Spawn a temporary pi session, feed it all provider summaries, and ask
    it to produce a unified memory document.  The result replaces memory.md.
    """
    snapshots = memory.get_all_snapshots()
    if not snapshots:
        return ""

    sections = [f"### {p}\n{c.strip()}" for p, c in snapshots]
    prompt = (
        "Below are handoff summaries from coding sessions using different "
        "AI providers.  Synthesise them into a single, coherent memory "
        "document that covers:\n"
        "- Project goals and overall context\n"
        "- Key decisions and rationale\n"
        "- Code and architectural changes\n"
        "- Current state and next steps\n\n"
        "Summaries:\n\n" + "\n\n".join(sections) + "\n\n"
        "Produce the unified memory document now."
    )

    cmd  = [_resolve_cmd(pi_cmd), "--mode", "rpc", "--no-session"] + pi_extra
    proc = await PiProcess.spawn("consolidation", cmd)
    text = ""
    try:
        await proc.send_command({"type": "prompt", "message": prompt}, timeout=15)
        while True:
            event = await asyncio.wait_for(proc.event_queue.get(), timeout=120)
            if event is None:
                break
            et = event.get("type", "")
            if et == "message_update":
                ae = event.get("assistantMessageEvent", {})
                if ae.get("type") == "text_delta":
                    text += ae.get("delta", "")
            elif et == "agent_end":
                break
    finally:
        await proc.terminate()

    return text


# ─── FastAPI app factory ──────────────────────────────────────────────────────

def _parse_provider(model_str: str) -> str:
    """
    OpenCode sends only the model ID (not the provider prefix):
      "pi-anthropic"  →  "anthropic"
      "pi-openai"     →  "openai"
      "pi-agent"      →  "pi-agent"
    Falls back to "pi-agent" for unrecognised values.
    """
    return MODEL_TO_PROVIDER.get(model_str, "pi-agent")


def create_app(pi_cmd: str, pi_extra: list[str]) -> FastAPI:
    memory   = SharedMemory()
    registry = ProviderRegistry(pi_cmd, pi_extra, memory)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await registry.start()
        yield
        await registry.stop()

    app = FastAPI(title="LinkPi", version="2.0.0", lifespan=lifespan)

    # ── GET /v1/models ────────────────────────────────────────────────────────
    @app.get("/v1/models")
    async def list_models() -> JSONResponse:
        return JSONResponse({
            "object": "list",
            "data": [
                {
                    "id":       model_id,
                    "object":   "model",
                    "created":  0,
                    "owned_by": "pi-mono",
                }
                for model_id in MODEL_TO_PROVIDER
            ],
        })

    # ── POST /v1/chat/completions ─────────────────────────────────────────────
    @app.post("/v1/chat/completions", response_model=None)
    async def chat(request: Request) -> StreamingResponse | JSONResponse:
        body:      dict       = await request.json()
        messages:  list[dict] = body.get("messages", [])
        do_stream: bool       = body.get("stream", True)
        provider:  str        = _parse_provider(body.get("model", "pi-agent"))

        if not messages:
            return JSONResponse({"error": "messages is empty"}, status_code=400)

        try:
            proc = await registry.get(provider)
        except Exception as exc:
            log.exception("Failed to get pi process  provider=%s", provider)
            return JSONResponse({"error": str(exc)}, status_code=503)

        # ── build prompt for pi ───────────────────────────────────────────────
        user_msgs = [m for m in messages if m.get("role") == "user"]
        pi_count  = proc.user_message_count
        req_count = len(user_msgs)

        if pi_count == 0:
            # First turn: inject shared memory + any prior OpenCode history
            mem_ctx   = memory.get()
            hist_ctx  = _history_block(messages) if req_count > 1 else ""
            user_text = _last_user_text(messages)

            parts = []
            if mem_ctx:
                parts.append(
                    "[Shared memory from previous sessions]\n"
                    + mem_ctx
                    + "\n[End shared memory]"
                )
            if hist_ctx:
                parts.append(hist_ctx)
            parts.append(user_text)
            prompt = "\n\n".join(parts)

        else:
            # Ongoing session: forward only messages pi has not seen yet
            new_turns = user_msgs[pi_count:]
            if not new_turns:
                # Defensive: same last turn resent (e.g. OpenCode retry)
                new_turns = [user_msgs[-1]]
                proc.user_message_count = max(0, proc.user_message_count - 1)
            prompt = "\n\n".join(_text(m.get("content", "")) for m in new_turns)

        cid = uuid.uuid4().hex
        log.info(
            "Chat  provider=%-12s  pi_turns=%d→%d  prompt_len=%d",
            provider, pi_count, req_count, len(prompt),
        )

        if do_stream:
            return StreamingResponse(
                _locked_stream(proc, prompt, cid),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
            )

        # Non-streaming: collect then wrap
        full = ""
        async with proc.lock:
            async for raw in _stream_prompt(proc, prompt, cid):
                if raw.startswith("data: {"):
                    try:
                        full += json.loads(raw[6:])["choices"][0]["delta"].get(
                            "content", ""
                        )
                    except Exception:
                        pass

        return JSONResponse({
            "id":      f"chatcmpl-{cid}",
            "object":  "chat.completion",
            "created": int(time.time()),
            "model":   body.get("model", "pi-agent"),
            "choices": [{
                "index":         0,
                "message":       {"role": "assistant", "content": full},
                "finish_reason": "stop",
            }],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        })

    # ── POST /v1/consolidate ──────────────────────────────────────────────────
    @app.post("/v1/consolidate")
    async def consolidate() -> JSONResponse:
        """
        Ask pi to synthesise all provider summaries into a single unified
        memory document.  The result replaces ~/.linkpi/memory.md and will
        be injected into any new session from this point on.
        """
        result = await _consolidate(pi_cmd, pi_extra, memory)
        if result:
            memory.set(result)
            return JSONResponse({"status": "consolidated", "chars": len(result)})
        return JSONResponse({"status": "nothing_to_consolidate"})

    # ── GET /v1/memory ────────────────────────────────────────────────────────
    @app.get("/v1/memory")
    async def get_memory() -> JSONResponse:
        """Inspect current shared memory and snapshot count."""
        return JSONResponse({
            "memory":         memory.get(),
            "snapshot_count": len(memory.get_all_snapshots()),
            "memory_file":    str(memory._memory_file),
        })

    return app


# ─── Entry point ─────────────────────────────────────────────────────────────

def main() -> None:
    p = argparse.ArgumentParser(
        description="LinkPi v2 – pi-mono OpenAI bridge with cross-provider memory"
    )
    p.add_argument("--host",     default="127.0.0.1")
    p.add_argument("--port",     type=int, default=8765)
    p.add_argument("--pi-cmd",   default="pi",
                   help="path to the pi executable (default: pi)")
    p.add_argument("--model",    default=None,
                   help="default model inside pi, e.g. anthropic/claude-sonnet-4")
    p.add_argument("--thinking", default=None,
                   choices=["off", "minimal", "low", "medium", "high", "xhigh"])
    args = p.parse_args()

    extra: list[str] = []
    if args.model:
        extra += ["--model", args.model]
    if args.thinking:
        extra += ["--thinking", args.thinking]

    log.info("=" * 64)
    log.info("LinkPi v2  –  pi-mono OpenAI bridge + cross-provider memory")
    log.info("Listening:      http://%s:%d", args.host, args.port)
    log.info("Pi command:     %s %s", args.pi_cmd, " ".join(extra))
    log.info("Memory store:   %s", LINKPI_DIR)
    log.info("")
    log.info("opencode.json  (place next to your project or in ~/.config/opencode/):")
    log.info(
        json.dumps({
            "$schema": "https://opencode.ai/config.schema.json",
            "model":   "link-pi/pi-agent",
            "provider": {
                "link-pi": {
                    "options": {
                        "baseURL": f"http://{args.host}:{args.port}/v1",
                        "apiKey":  "local",
                    },
                    "models": {
                        mid: {"name": f"Pi \u2192 {mid.removeprefix('pi-').capitalize()}"}
                        for mid in MODEL_TO_PROVIDER
                    },
                }
            },
        }, indent=2)
    )
    log.info("")
    log.info("Available models (switch in OpenCode model selector Ctrl+M):")
    for mid in MODEL_TO_PROVIDER:
        log.info("  link-pi/%s", mid)
    log.info("")
    log.info("Extra endpoints:")
    log.info("  POST http://%s:%d/v1/consolidate  – synthesise unified memory",
             args.host, args.port)
    log.info("  GET  http://%s:%d/v1/memory       – inspect current memory",
             args.host, args.port)
    log.info("=" * 64)

    uvicorn.run(create_app(args.pi_cmd, extra), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
