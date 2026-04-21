<!-- OSS_WEEKEND_START -->
# 🏖️ OSS Weekend

**Issue tracker reopens Monday, April 6, 2026.**

OSS weekend runs Friday, March 27, 2026 through Monday, April 6, 2026. New issues are auto-closed during this time. For support, join [Discord](https://discord.com/invite/3cU7Bz4UPx).
<!-- OSS_WEEKEND_END -->

---

<p align="center">
  <a href="https://shittycodingagent.ai">
    <img src="https://shittycodingagent.ai/logo.svg" alt="pi logo" width="128">
  </a>
</p>
<p align="center">
  <a href="https://discord.com/invite/3cU7Bz4UPx"><img alt="Discord" src="https://img.shields.io/badge/discord-community-5865F2?style=flat-square&logo=discord&logoColor=white" /></a>
  <a href="https://github.com/badlogic/pi-mono/actions/workflows/ci.yml"><img alt="Build status" src="https://img.shields.io/github/actions/workflow/status/badlogic/pi-mono/ci.yml?style=flat-square&branch=main" /></a>
</p>
<p align="center">
  <a href="https://pi.dev">pi.dev</a> domain graciously donated by
  <br /><br />
  <a href="https://exe.dev"><img src="packages/coding-agent/docs/images/exy.png" alt="Exy mascot" width="48" /><br />exe.dev</a>
</p>

**Language:** English | [繁體中文](README.zh-TW.md)

---

# Pi Monorepo

> **Looking for the pi coding agent?** See **[packages/coding-agent](packages/coding-agent)** for installation and usage.

Tools for building AI agents and managing LLM deployments.

## Packages

| Package | Description |
|---------|-------------|
| **[@mariozechner/pi-ai](packages/ai)** | Unified multi-provider LLM API (OpenAI, Anthropic, Google, etc.) |
| **[@mariozechner/pi-agent-core](packages/agent)** | Agent runtime with tool calling and state management |
| **[@mariozechner/pi-coding-agent](packages/coding-agent)** | Interactive coding agent CLI |
| **[@mariozechner/pi-mom](packages/mom)** | Slack bot that delegates messages to the pi coding agent |
| **[@mariozechner/pi-tui](packages/tui)** | Terminal UI library with differential rendering |
| **[@mariozechner/pi-web-ui](packages/web-ui)** | Web components for AI chat interfaces |
| **[@mariozechner/pi-pods](packages/pods)** | CLI for managing vLLM deployments on GPU pods |

## Harness Engineering（駕馭工程）

[`harness/`](harness) 目錄包含定義 Agent 行為的核心設定檔，實踐「MD as Code」工作模式。這些 Markdown 檔案定義了雙 Agent 架構的分工邏輯與行為護欄。

### 雙 Agent 架構

```
強尼（指揮官）
  │
  │  發出命令
  ▼
大寶（Router）         ← pi agent（雲端 LLM：Anthropic / OpenAI / Google）
  │
  │  分析任務 → 分派指令
  ▼
小寶（助手）           ← 本地 Gemma 4 31B（localhost:8080）
  │
  │  完成後回報
  ▼
大寶（Router）
  │
  │  檢查品質 → 回報結果
  ▼
強尼（指揮官）
```

| Agent | 角色 | LLM Provider | 權限 |
|-------|------|--------------|------|
| **大寶** | 任務分析、分派、品質檢查、Git 操作、最終回報 | pi agent（雲端 LLM） | 可執行 git push |
| **小寶** | 程式碼編寫、開發、測試 | 本地 Gemma 4 31B | 禁止 git push |

### 核心設定檔

| 檔案 | 說明 |
|------|------|
| [`agents.md`](harness/agents.md) | Agent 定義：身份、能力邊界、觸發條件、權限矩陣 |
| [`rule.md`](harness/rule.md) | 全局行為護欄：禁止行為、錯誤處理、操作確認規則 |
| [`memory.md`](harness/memory.md) | 記憶管理：來源、優先順序、儲存格式、提取規則 |
| [`tests.md`](harness/tests.md) | 測試框架：核心測試案例與評估標準 |
| [`mock.md`](harness/mock.md) | 外部依賴模擬：服務清單、錯誤處理、重試策略 |
| [`skills.md`](harness/skills.md) | 技能清單：可用工具與危險操作標記 |

### 小寶 Agent Client

[`harness/xiaobao.py`](harness/xiaobao.py) 是小寶的 Python 實作，使用 ACTION/PARAMS 文字格式進行工具呼叫：

```bash
# 啟動本地 Gemma 4（前置條件）
vmlx serve dealignai/Gemma-4-31B-JANG_4M-CRACK --port 8080

# 使用小寶執行任務
python3 harness/xiaobao.py --task "寫一個 Python 腳本" --workdir .
```

### Gemma 4 31B 本地部署

詳見 [`SetGemma4LLM.md`](SetGemma4LLM.md)，包含：
- macOS + Apple Silicon 安裝步驟
- vMLX 推理引擎設定
- Open WebUI 聊天介面
- 疑難排解

---

## LinkPi – OpenCode (VS Code) Bridge

[`LinkPi.py`](LinkPi.py) is a Python middleware that exposes pi's agent as an OpenAI-compatible HTTP API, allowing [OpenCode](https://opencode.ai) (VS Code extension) to use pi as its coding agent backend.

Each LLM provider gets its own persistent pi session and session directory. Switching providers in OpenCode's model selector automatically compacts the outgoing session, extracts a handoff summary, and injects it as context into the incoming provider's session. A `/v1/consolidate` endpoint asks pi itself to synthesise all provider summaries into a single unified memory document.

### Architecture

```
OpenCode (VS Code)
  POST /v1/chat/completions
  model: "link-pi/<provider>"   ← provider encoded in model name
          │
          ▼
  LinkPi.py  (FastAPI, port 8765)
    │
    ├── ProviderRegistry
    │     one PiProcess per provider, each with its own session directory
    │     detects provider switch → compact outgoing → update SharedMemory
    │
    ├── SharedMemory  (~/.linkpi/memory.md)
    │     cross-provider context injected at the start of every new session
    │
    └── /v1/consolidate
          spawns a fresh pi session, feeds it all summaries,
          asks it to produce one unified memory document
    │
    │  JSONL over stdin/stdout  (pi RPC protocol)
    ▼
  pi --mode rpc  (one subprocess per provider)
    │  --session-dir ~/.linkpi/sessions/<provider>/
    ▼
  LLM provider  (Anthropic / OpenAI / Google / …)
```

### Memory flow

```
User switches from Anthropic → OpenAI in OpenCode model selector
  1. LinkPi compacts the Anthropic pi session
  2. Pi returns a handoff summary (plain text)
  3. Summary appended to ~/.linkpi/memory.md
  4. OpenAI pi session starts; shared memory is prepended
     to the first user message as a [Context] block
  5. OpenAI continues work with full awareness of what Anthropic did

POST /v1/consolidate
  Spawns a temporary pi session, feeds it ALL provider summaries,
  asks it to synthesise a single unified memory document → replaces memory.md
```

### Setup

#### 1. Install Python dependencies

```bash
pip install fastapi uvicorn
```

#### 2. Prepare the pi executable

**If pi is installed globally** (`npm install -g @mariozechner/pi-coding-agent`):

```bash
# Linux/macOS
python LinkPi.py

# Windows — npm global scripts are .cmd wrappers
python LinkPi.py --pi-cmd pi.cmd
```

**If running from source (this monorepo):**

Linux/macOS — use `pi-test.sh`:
```bash
python LinkPi.py --pi-cmd ./pi-test.sh
```

Windows — the repo root already includes `pi.cmd`. It operates in two modes:

- **No arguments** (e.g. double-clicking the shortcut): runs `pi_startup.py`, which starts LinkPi in the background, schedules hourly GitHub auto-sync, then launches the pi interactive interface in the foreground. Closing the pi window also shuts down LinkPi.
- **With arguments** (e.g. `pi --mode rpc ...` called by LinkPi internally): runs the pi CLI directly, bypassing the startup logic.

To start LinkPi manually (no auto-sync, no desktop shortcut):
```cmd
python LinkPi.py --pi-cmd pi.cmd
```

#### Daily startup shortcut (Windows)

Drag `pi.cmd` from the repo root to your desktop. Double-clicking it will:
1. Start LinkPi server (bound to `0.0.0.0:8765`).
2. Start a background thread that auto-commits and pushes changes every hour.
3. Open the pi interactive interface in the foreground.
4. Shut down LinkPi when you close the pi window.

The startup script is [`pi_startup.py`](pi_startup.py) at the repo root.

**Faster startup (optional but recommended):** By default `pi_startup.py` launches pi via `tsx` which compiles TypeScript on-the-fly every run. Build once to get instant startup:

```bash
cd packages/coding-agent && npm run build
```

After building, `pi_startup.py` automatically uses the compiled `dist/cli.js` instead of tsx. Re-run `npm run build` whenever source files change.

> **Windows `node_modules` note:** If `node_modules` was installed under WSL/Linux, native binaries (esbuild, etc.) are Linux-only. Fix by running `npm install` from a Windows terminal. If permission errors occur on `.bin/`, delete it first from WSL (`rm -rf node_modules/.bin`), then run `npm install` from Windows.

#### 3. Configure local LLM providers (optional)

To add a self-hosted model (Ollama, vLLM, LM Studio), create `~/.pi/agent/models.json`:

- **Windows:** `C:\Users\<username>\.pi\agent\models.json`
- **Linux/macOS:** `~/.pi/agent/models.json`

First check what models your server exposes:
```bash
curl http://<your-server>/v1/models
```

**Required fields for custom models:**
- `baseUrl` — endpoint of your local server
- `apiKey` — any non-empty string for unauthenticated servers (e.g. `"none"`)
- `api` — must be set at provider **or** model level; omitting it causes a startup error. Valid values: `"openai-completions"`, `"openai-responses"`, `"anthropic-messages"`

Example for a vLLM server running Qwen3-Coder:
```json
{
  "providers": {
    "local-llm": {
      "baseUrl": "http://192.168.249.11:8060/v1",
      "api": "openai-completions",
      "apiKey": "local",
      "compat": {
        "supportsDeveloperRole": false,
        "supportsReasoningEffort": false,
        "supportsUsageInStreaming": false,
        "maxTokensField": "max_tokens",
        "thinkingFormat": "qwen-chat-template"
      },
      "models": [
        {
          "id": "qwen3-coder",
          "name": "Qwen3-Coder 30B (Local)",
          "reasoning": true,
          "input": ["text"],
          "contextWindow": 100000,
          "maxTokens": 16384,
          "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
        }
      ]
    }
  }
}
```

Verify pi can see the model (the file reloads automatically when opening `/model`):
```bash
pi --list-models local-llm
# provider   model        context  max-out  thinking  images
# local-llm  qwen3-coder  100K     16.4K    yes       no
```

The `pi-local` model in LinkPi routes to this `local-llm` provider. To change the provider name, update `MODEL_TO_PROVIDER` in `LinkPi.py`.

#### 4. Configure opencode.json

Place `opencode.json` next to your project (or at `~/.config/opencode/config.json` for global use):

```json
{
  "$schema": "https://opencode.ai/config.schema.json",
  "model": "link-pi/pi-local",
  "provider": {
    "link-pi": {
      "options": {
        "baseURL": "http://127.0.0.1:8765/v1",
        "apiKey":  "local"
      },
      "models": {
        "pi-anthropic": { "name": "Pi \u2192 Anthropic" },
        "pi-openai":    { "name": "Pi \u2192 OpenAI" },
        "pi-google":    { "name": "Pi \u2192 Google" },
        "pi-groq":      { "name": "Pi \u2192 Groq" },
        "pi-mistral":   { "name": "Pi \u2192 Mistral" },
        "pi-bedrock":   { "name": "Pi \u2192 Bedrock" },
        "pi-vertex":    { "name": "Pi \u2192 Vertex" },
        "pi-openrouter":{ "name": "Pi \u2192 OpenRouter" },
        "pi-local":     { "name": "Pi \u2192 Local (vLLM/Ollama)" },
        "pi-agent":     { "name": "Pi (default)" }
      }
    }
  }
}
```

LinkPi prints a config snippet on startup. Switch providers via OpenCode's model selector (`Ctrl+M`).

#### 5. Verify the setup

```bash
# 1. LinkPi is running
curl http://127.0.0.1:8765/v1/models

# 2. Pi subprocess can start
curl http://127.0.0.1:8765/v1/memory

# 3. End-to-end: LinkPi -> pi -> LLM
curl -s http://127.0.0.1:8765/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"pi-local","stream":false,"messages":[{"role":"user","content":"reply with just PONG"}]}'
```

> **Why `options.baseURL` instead of top-level `baseURL`?**  
> OpenCode's provider schema uses `.strict()` — only `name`, `npm`, `models`, `options`, `whitelist`, `blacklist` are allowed at the top level. `baseURL` and `apiKey` must be nested inside `options`. Placing them at the top level causes the `Unrecognized keys` validation error.

### Available models

Switch providers by changing `model` in `opencode.json`, or use OpenCode's model selector (`Ctrl+M`).

| Model (`link-pi/<id>`) | Pi provider used |
|------------------------|------------------|
| `pi-anthropic` | `--provider anthropic` |
| `pi-openai` | `--provider openai` |
| `pi-google` | `--provider google` |
| `pi-groq` | `--provider groq` |
| `pi-mistral` | `--provider mistral` |
| `pi-bedrock` | `--provider bedrock` |
| `pi-vertex` | `--provider vertex` |
| `pi-openrouter` | `--provider openrouter` |
| `pi-local` | `local-llm` (via `~/.pi/agent/models.json`) |
| `pi-agent` | pi chooses provider |

### CLI options

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | `127.0.0.1` | Bind address |
| `--port` | `8765` | Port |
| `--pi-cmd` | `pi` | Path to the pi executable |
| `--model` | *(pi default)* | Default model inside pi, e.g. `anthropic/claude-sonnet-4` |
| `--thinking` | *(pi default)* | Thinking level: `off` `minimal` `low` `medium` `high` `xhigh` |

### Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /v1/models` | List all `link-pi/<provider>` models |
| `POST /v1/chat/completions` | OpenAI-compatible streaming chat |
| `POST /v1/consolidate` | Ask pi to synthesise all provider summaries into one unified memory |
| `GET /v1/memory` | Inspect current shared memory and snapshot count |

### How it works

- **One pi subprocess per provider.** Each `link-pi/<provider>` model maps to a long-lived `pi --mode rpc` process with its own `--session-dir ~/.linkpi/sessions/<provider>/`. Pi's full session persistence (branching, compaction, `/tree`) works normally within each provider.
- **Provider switch = memory handoff.** When OpenCode switches to a different model, LinkPi compacts the outgoing session (using pi's `compact` RPC command with handoff-optimised instructions), extracts the summary, and appends it to `~/.linkpi/memory.md`.
- **Shared memory injection.** Every new session starts with the full contents of `memory.md` prepended to the first user message as a `[Shared memory from previous sessions]` block. The new provider has complete awareness of prior work.
- **Consolidation on demand.** `POST /v1/consolidate` spawns a temporary pi session, feeds it all accumulated provider summaries, and asks pi to synthesise them into a single coherent memory document that replaces `memory.md`.
- **Response routing via Future.** Pi RPC command responses (e.g. the prompt ack, compact result) are routed to `asyncio.Future` objects keyed by id, separate from the streaming event queue. This lets `compact` run synchronously during a provider switch without interfering with streaming.
- **Tool execution is visible.** Pi's autonomous `bash`, `read`, `edit` calls are streamed to OpenCode as italic annotations so the user can follow along.
- **Auth stays with pi.** API keys and OAuth tokens are managed by pi (`~/.pi/agent/auth.json` or env vars). The `apiKey: "local"` in OpenCode's config is a placeholder.

### Known limitations

| Limitation | Detail |
|------------|--------|
| Compact requires enough context | Pi's compact command needs sufficient conversation history; very short sessions produce no summary. |
| Provider switch blocks the next request | The first request after a switch waits for the outgoing session to compact before proceeding. |
| Tool calls are opaque to OpenCode | OpenCode sees plain text, not structured `tool_call`/`tool_result` blocks. |
| One request at a time per provider | Concurrent requests to the same provider are serialised via `asyncio.Lock`. |
| Windows subprocess | Requires pi to be on `PATH`; adjust `--pi-cmd` if needed. |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines and [AGENTS.md](AGENTS.md) for project-specific rules (for both humans and agents).

## Development

```bash
npm install          # Install all dependencies
npm run build        # Build all packages
npm run check        # Lint, format, and type check
./test.sh            # Run tests (skips LLM-dependent tests without API keys)
./pi-test.sh         # Run pi from sources (can be run from any directory)
```

> **Note:** `npm run check` requires `npm run build` to be run first. The web-ui package uses `tsc` which needs compiled `.d.ts` files from dependencies.

## License

MIT
