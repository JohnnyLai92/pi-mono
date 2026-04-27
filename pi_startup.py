import subprocess
import threading
import time
import os
import datetime
import sys
import json

# Ensure UTF-8 output on Windows (prevents UnicodeEncodeError with emoji/CJK)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# 設定 Agent 目錄環境變數
PI_CONFIG_ROOT = os.path.expanduser("~/.pi")
AGENT_DIR = os.path.join(PI_CONFIG_ROOT, "agent")
os.environ["PI_CODING_AGENT_DIR"] = AGENT_DIR
USER_MODELS_JSON = os.path.join(PI_CONFIG_ROOT, "agent", "models.json")
PROJECT_MODELS_JSON = os.path.join(os.path.dirname(__file__), "packages", "pods", "models.json")

if os.path.exists(USER_MODELS_JSON):
    MODELS_JSON_PATH = USER_MODELS_JSON
else:
    MODELS_JSON_PATH = PROJECT_MODELS_JSON

MERIDIAN_PROVIDER = {
    "baseUrl": "http://127.0.0.1:3456",
    "apiKey": "x",
    "api": "anthropic-messages",
    "models": [
        {"id": "claude-sonnet-4-6", "name": "Claude Sonnet 4.6 (Meridian)"},
        {"id": "claude-opus-4-6",   "name": "Claude Opus 4.6 (Meridian)"},
    ]
}

# ---------------------------------------------------------------------------
# Meridian helpers
# ---------------------------------------------------------------------------

def add_meridian_to_models_json():
    try:
        with open(MODELS_JSON_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        config.setdefault("providers", {})["meridian"] = MERIDIAN_PROVIDER
        with open(MODELS_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception: pass

def remove_meridian_from_models_json():
    try:
        with open(MODELS_JSON_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        if config.get("providers", {}).pop("meridian", None) is not None:
            with open(MODELS_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception: pass

# ---------------------------------------------------------------------------
# STM state helpers
# ---------------------------------------------------------------------------

def load_stm_state(stm_state_file):
    try:
        with open(stm_state_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_stm_state(stm_state_file, state):
    try:
        with open(stm_state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception: pass

def has_stm_content(stm_dir):
    if not os.path.exists(stm_dir):
        return False
    return any(f.endswith(".md") for f in os.listdir(stm_dir))

# ---------------------------------------------------------------------------
# Startup: warn if there is un-consolidated STM from a previous day
# ---------------------------------------------------------------------------

def check_pending_consolidation(stm_dir, stm_state_file):
    if not has_stm_content(stm_dir):
        return
    today = datetime.date.today().isoformat()
    state = load_stm_state(stm_state_file)
    if state.get("last_consolidated_date") == today:
        return
    old_files = [
        f for f in os.listdir(stm_dir)
        if f.endswith(".md") and not f.startswith(today)
    ]
    if old_files:
        last = state.get("last_consolidated_date", "從未")
        print(f"\n[小白報報] ⚠️  發現 {len(old_files)} 個未彙整的 STM 記憶（上次彙整：{last}）")
        print("[小白報報] 💡 請優先在 pi 中執行：consolidate_memory\n")

# ---------------------------------------------------------------------------
# Background: 17:00 consolidation reminder (only when STM has content)
# ---------------------------------------------------------------------------

def memory_summary_scheduler(stm_dir, stm_state_file):
    while True:
        now = datetime.datetime.now()
        if now.hour == 17 and now.minute == 0:
            today = datetime.date.today().isoformat()
            state = load_stm_state(stm_state_file)
            if state.get("last_consolidated_date") != today and has_stm_content(stm_dir):
                print("\n[小白報報] ⏰ 17:00 記憶彙整提醒！今日有未彙整的 STM 記憶。")
                print("[小白報報] 💡 請在 pi 中執行 consolidate_memory，完成後系統將清除 STM 並更新 LTM\n")
            time.sleep(61)
        time.sleep(30)

# ---------------------------------------------------------------------------
# Background: auto git sync
# ---------------------------------------------------------------------------

def auto_sync_github():
    while True:
        time.sleep(3600)
        try:
            repo_dir = os.path.dirname(os.path.abspath(__file__))
            status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=repo_dir)
            if status.stdout.strip():
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                subprocess.run(["git", "add", "."], check=True, cwd=repo_dir)
                subprocess.run(["git", "commit", "-m", f"Auto-sync: {now}"], check=True, cwd=repo_dir)
                subprocess.run(["git", "push", "origin", "main"], check=True, cwd=repo_dir)
        except Exception: pass

# ---------------------------------------------------------------------------
# Notion reminder
# ---------------------------------------------------------------------------

def remind_notion_tasks():
    try:
        from dotenv import load_dotenv
        load_dotenv()
        from packages.mom.src.skills.notion_reader import NotionSkill
        last_date_file = os.path.join(PI_CONFIG_ROOT, "last_notion_remind.txt")
        today_str = datetime.date.today().isoformat()
        if os.path.exists(last_date_file):
            with open(last_date_file, "r", encoding="utf-8") as f:
                if f.read().strip() == today_str: return
        print("\n[小白報報] 📝 正在為您抓取今日 Notion 未完成工作...")
        skill = NotionSkill()
        tasks = skill.get_unfinished_tasks()
        if isinstance(tasks, list) and len(tasks) > 0 and "error" not in tasks[0]:
            print("--- 📌 Notion 未完成待辦清單 ---")
            for task in tasks:
                print(f"🔹 [{task['status']}] {task['title']} \n   🔗 {task['url']}")
            print("-------------------------------\n")
            with open(last_date_file, "w", encoding="utf-8") as f: f.write(today_str)
        else:
            print("[小白報報] ✨ 目前沒有未完成的 Notion 任務。")
            with open(last_date_file, "w", encoding="utf-8") as f: f.write(today_str)
    except Exception as e:
        print(f"[小白報報] ⚠️ Notion 提醒出錯: {e}")

# ---------------------------------------------------------------------------
# Post-session: auto-capture session log to STM if agent did not write one
# Source: ~/.pi/agent/sessions/{cwd-slug}/*.jsonl (always created by pi CLI)
# ---------------------------------------------------------------------------

def _cwd_to_session_slug(cwd):
    """Convert a path to the session directory slug pi uses.

    Matches session-manager.ts line 422:
      `--${cwd.replace(/^[/\\]/, "").replace(/[/\\:]/g, "-")}--`
    e.g. C:\\Projects\\github\\pi-mono → --C--Projects-github-pi-mono--
    """
    import re
    stripped = re.sub(r'^[/\\]', '', cwd)
    safe = re.sub(r'[/\\:]', '-', stripped)
    return f'--{safe}--'

def _extract_messages_from_jsonl(jsonl_path):
    """Return list of (role, text) from a pi session JSONL file."""
    msgs = []
    try:
        with open(jsonl_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                if obj.get("type") != "message":
                    continue
                msg = obj.get("message", {})
                role = msg.get("role", "")
                if role not in ("user", "assistant"):
                    continue
                content = msg.get("content", "")
                if isinstance(content, list):
                    text = " ".join(
                        c.get("text", "") for c in content
                        if isinstance(c, dict) and c.get("type") == "text"
                    )
                else:
                    text = str(content)
                text = text.strip()
                if text:
                    msgs.append((role, text))
    except Exception:
        pass
    return msgs

def capture_session_to_stm(pi_dir, stm_dir, force=False):
    """Summarize today's JSONL sessions into a single STM markdown file.

    Args:
        force: if True, overwrite today's existing auto STM (used by watcher
               for incremental updates).
    """
    today = datetime.date.today().isoformat()

    # Skip if agent already wrote a manual STM file today (unless force=True).
    # Manual files don't end with `_auto.md`; we never overwrite them.
    existing_today = [
        f for f in (os.listdir(stm_dir) if os.path.exists(stm_dir) else [])
        if f.endswith(".md") and f.startswith(today)
    ]
    manual_today = [f for f in existing_today if not f.endswith("_auto.md")]
    if manual_today:
        return
    if existing_today and not force:
        return

    # Locate today's JSONL session files (pi CLI always creates these)
    slug = _cwd_to_session_slug(pi_dir)
    session_dir = os.path.join(PI_CONFIG_ROOT, "agent", "sessions", slug)
    if not os.path.exists(session_dir):
        return

    today_prefix = today + "T"
    today_files = sorted(
        f for f in os.listdir(session_dir)
        if f.startswith(today_prefix) and f.endswith(".jsonl")
    )
    if not today_files:
        return

    # Collect all messages across today's sessions (cap at 6000 chars for prompt)
    all_lines = []
    for fname in today_files:
        msgs = _extract_messages_from_jsonl(os.path.join(session_dir, fname))
        for role, text in msgs:
            label = "強尼" if role == "user" else "Agent"
            all_lines.append(f"[{label}] {text[:300]}")

    if not all_lines:
        return

    conversation_text = "\n".join(all_lines)
    if len(conversation_text) > 6000:
        conversation_text = conversation_text[:6000] + "\n...(截斷)"

    print(f"\n[小白報報] 📝 偵測到今日 {len(today_files)} 個 session，自動生成 STM 摘要...")
    prompt = (
        f"以下是今日（{today}）與 pi agent 的對話紀錄摘錄（共 {len(all_lines)} 則訊息）。\n"
        "請生成一份簡潔的 STM（短期記憶）摘要，格式如下：\n\n"
        f"# STM: {today} 自動摘要\n\n"
        "## 重要決策\n- ...\n\n"
        "## 關鍵發現\n- ...\n\n"
        "## 待辦事項\n- [ ] ...\n\n"
        "## 已完成\n- [x] ...\n\n"
        "規則：只記錄結果與重點，不記錄原始對話。使用繁體中文。\n\n"
        f"對話紀錄：\n{conversation_text}"
    )
    try:
        # On Windows, `claude` is `claude.cmd`; resolve it explicitly so we
        # can pass the multi-line prompt via stdin (avoids shell-quoting issues).
        import shutil
        claude_bin = shutil.which("claude") or shutil.which("claude.cmd") or "claude"
        result = subprocess.run(
            [claude_bin, "-p"],
            input=prompt,
            capture_output=True, text=True, encoding="utf-8",
            cwd=pi_dir, timeout=120,
        )
        if result.returncode == 0 and result.stdout.strip():
            os.makedirs(stm_dir, exist_ok=True)
            # Stable filename per day so watcher overwrites instead of
            # accumulating dozens of partial files.
            stm_file = os.path.join(stm_dir, f"{today}_auto.md")
            with open(stm_file, "w", encoding="utf-8") as f:
                f.write(result.stdout.strip())
            print(f"[小白報報] ✅ STM 自動摘要已寫入：{os.path.basename(stm_file)}")
        else:
            print(f"[小白報報] ⚠️ 自動摘要失敗（exit {result.returncode}）")
    except Exception as e:
        print(f"[小白報報] ⚠️ 自動生成 STM 摘要失敗：{e}")


# ---------------------------------------------------------------------------
# Background: STM watcher — every N seconds, if today's JSONL has new content,
# regenerate the STM auto-summary. Prevents data loss on crash / forced kill.
# ---------------------------------------------------------------------------

def stm_watcher(pi_dir, stm_dir, interval=600):
    """Re-run capture_session_to_stm whenever today's JSONL files change."""
    slug = _cwd_to_session_slug(pi_dir)
    session_dir = os.path.join(PI_CONFIG_ROOT, "agent", "sessions", slug)
    sig_dir = os.path.join(pi_dir, ".pi")
    os.makedirs(sig_dir, exist_ok=True)

    while True:
        time.sleep(interval)
        try:
            today = datetime.date.today().isoformat()
            if not os.path.exists(session_dir):
                continue
            today_prefix = today + "T"
            today_files = [
                f for f in os.listdir(session_dir)
                if f.startswith(today_prefix) and f.endswith(".jsonl")
            ]
            if not today_files:
                continue
            # Signature = sum of (mtime, size) of today's JSONL files.
            sig_parts = []
            for fname in today_files:
                p = os.path.join(session_dir, fname)
                st = os.stat(p)
                sig_parts.append(f"{fname}:{int(st.st_mtime)}:{st.st_size}")
            sig = "|".join(sorted(sig_parts))

            sig_file = os.path.join(sig_dir, f"stm_watcher_{today}.sig")
            prev_sig = ""
            if os.path.exists(sig_file):
                with open(sig_file, "r", encoding="utf-8") as f:
                    prev_sig = f.read().strip()
            if sig == prev_sig:
                continue  # No new content since last check

            print(f"\n[小白報報] 🔄 STM watcher：偵測到 JSONL 變化，更新今日摘要...")
            capture_session_to_stm(pi_dir, stm_dir, force=True)
            with open(sig_file, "w", encoding="utf-8") as f:
                f.write(sig)
        except Exception as e:
            print(f"[小白報報] ⚠️ STM watcher 出錯：{e}")

# ---------------------------------------------------------------------------
# Build APPEND_SYSTEM.md: LTM + STM → project-level path (loaded by agent)
# ---------------------------------------------------------------------------

def rebuild_append_system(pi_dir, memory_dir, stm_dir, append_system_path):
    sections = []

    # LTM
    if os.path.exists(memory_dir):
        ltm_contents = []
        for filename in sorted(os.listdir(memory_dir)):
            if filename.endswith(".md"):
                try:
                    with open(os.path.join(memory_dir, filename), "r", encoding="utf-8") as f:
                        c = f.read().strip()
                    if c:
                        ltm_contents.append(f"### Memory: {filename}\n{c}\n")
                except Exception as e:
                    print(f"[小白報報] ⚠️ 無法讀取記憶檔 {filename}: {e}")
        if ltm_contents:
            sections.append("# User Memory / Preferences (LTM)\n\n" + "\n".join(ltm_contents))
        print(f"[小白報報] 🧠 LTM：已載入 {len(ltm_contents)} 個記憶檔")

    # STM
    if os.path.exists(stm_dir):
        stm_contents = []
        for filename in sorted(os.listdir(stm_dir)):
            if filename.endswith(".md"):
                try:
                    with open(os.path.join(stm_dir, filename), "r", encoding="utf-8") as f:
                        c = f.read().strip()
                    if c:
                        stm_contents.append(f"### STM: {filename}\n{c}\n")
                except Exception as e:
                    print(f"[小白報報] ⚠️ 無法讀取 STM 檔 {filename}: {e}")
        if stm_contents:
            sections.append("# Recent Session Context (STM)\n\n" + "\n".join(stm_contents))
            print(f"[小白報報] 📝 STM：已載入 {len(stm_contents)} 個短期記憶")

    with open(append_system_path, "w", encoding="utf-8") as f:
        f.write("\n\n---\n\n".join(sections))

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pi_dir = os.path.dirname(os.path.abspath(__file__))

    memory_dir    = os.path.join(PI_CONFIG_ROOT, "memory")
    stm_dir       = os.path.join(pi_dir, ".pi", "short_term_memory")
    stm_state_file = os.path.join(pi_dir, ".pi", "stm_state.json")
    # resource-loader.ts checks {cwd}/.pi/APPEND_SYSTEM.md first
    append_system_path = os.path.join(pi_dir, ".pi", "APPEND_SYSTEM.md")

    # --- CLI: --flush-stm-only ---
    # Manually trigger STM capture without launching pi agent.
    # Used by skill `stm_flush` and by user as `python pi_startup.py --flush-stm-only`.
    if "--flush-stm-only" in sys.argv:
        print("[小白報報] 🔄 手動 flush：彙整今日 JSONL → STM ...")
        capture_session_to_stm(pi_dir, stm_dir, force=True)
        sys.exit(0)

    print("[小白報報] 🐶 總司令腳本啟動！")

    # --- startup checks ---
    check_pending_consolidation(stm_dir, stm_state_file)

    meridian_process = None
    try:
        answer = input("[小白報報] 🔌 是否啟動 Meridian proxy？(y/N) ").strip().lower()
    except: answer = "n"
    if answer == "y":
        add_meridian_to_models_json()
        try:
            meridian_process = subprocess.Popen(
                ["meridian"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                env={**os.environ,
                     "CLAUDE_CONFIG_DIR": os.path.expanduser("~/.config/meridian"),
                     "MERIDIAN_DEFAULT_AGENT": "pi",
                     "CLAUDE_PROXY_PASSTHROUGH": "true"}
            )
        except: pass

    threading.Thread(target=auto_sync_github, daemon=True).start()
    threading.Thread(target=memory_summary_scheduler, args=(stm_dir, stm_state_file), daemon=True).start()
    # STM watcher: every 10 min, regenerate today's STM if JSONL changed.
    # Prevents data loss on crash / forced kill (no longer reliant on finally).
    threading.Thread(target=stm_watcher, args=(pi_dir, stm_dir, 600), daemon=True).start()

    linkpi_process = None
    try:
        linkpi_answer = input("[小白報報] 🔌 是否啟動 LinkPi 伺服器 (port 8765)？(y/N) ").strip().lower()
    except: linkpi_answer = "n"
    if linkpi_answer == "y":
        try:
            linkpi_process = subprocess.Popen(
                [sys.executable, "LinkPi.py", "--host", "0.0.0.0"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=pi_dir
            )
        except: pass

    scheduler_process = None
    if os.path.exists(os.path.join(pi_dir, "pi_scheduler.py")):
        try:
            scheduler_process = subprocess.Popen(
                [sys.executable, "pi_scheduler.py"],
                stdout=open(os.path.join(pi_dir, "scheduler_output.log"), "a", encoding="utf-8"),
                stderr=open(os.path.join(pi_dir, "scheduler_error.log"), "a", encoding="utf-8"),
                cwd=pi_dir
            )
        except: pass

    # Build context for agent
    rebuild_append_system(pi_dir, memory_dir, stm_dir, append_system_path)
    remind_notion_tasks()

    node_cmd = "node"
    cli_js  = os.path.join(pi_dir, "packages", "coding-agent", "dist", "cli.js")
    tsx_mjs = os.path.join(pi_dir, "node_modules", "tsx", "dist", "cli.mjs")
    cli_ts  = os.path.join(pi_dir, "packages", "coding-agent", "src", "cli.ts")
    launch_cmd = [node_cmd, cli_js] if os.path.exists(cli_js) else [node_cmd, tsx_mjs, cli_ts]

    try:
        subprocess.run(launch_cmd, check=True, cwd=pi_dir)
    except: pass
    finally:
        # Post-session: auto-capture STM if agent did not write one
        capture_session_to_stm(pi_dir, stm_dir)
        # Rebuild context with fresh STM so next startup is up-to-date
        rebuild_append_system(pi_dir, memory_dir, stm_dir, append_system_path)
        if linkpi_process: linkpi_process.terminate()
        if scheduler_process: scheduler_process.terminate()
        if meridian_process: meridian_process.terminate()
        remove_meridian_from_models_json()
