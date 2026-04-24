import subprocess
import threading
import time
import os
import datetime
import sys
import json

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

def memory_summary_scheduler():
    while True:
        now = datetime.datetime.now()
        if now.hour == 17 and now.minute == 0:
            print("\n[小白報報] ⏰ 時間到了！現在是 17:00，是否需要我彙整今日的短期記憶並整理至長期記憶區？")
            time.sleep(61)
        time.sleep(30)

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

if __name__ == "__main__":
    print("[小白報報] 🐶 總司令腳本啟動！")
    pi_dir = os.path.dirname(os.path.abspath(__file__))
    meridian_process = None
    try:
        answer = input("[小白報報] 🔌 是否啟動 Meridian proxy？(y/N) ").strip().lower()
    except: answer = "n"
    if answer == "y":
        add_meridian_to_models_json()
        try:
            meridian_process = subprocess.Popen(["meridian"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env={**os.environ, "CLAUDE_CONFIG_DIR": os.path.expanduser("~/.config/meridian"), "MERIDIAN_DEFAULT_AGENT": "pi", "CLAUDE_PROXY_PASSTHROUGH": "true"})
        except: pass
    threading.Thread(target=auto_sync_github, daemon=True).start()
    threading.Thread(target=memory_summary_scheduler, daemon=True).start()
    linkpi_process = None
    try:
        linkpi_answer = input("[小白報報] 🔌 是否啟動 LinkPi 伺服器 (port 8765)？(y/N) ").strip().lower()
    except: linkpi_answer = "n"
    if linkpi_answer == "y":
        try:
            linkpi_process = subprocess.Popen([sys.executable, "LinkPi.py", "--host", "0.0.0.0"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=pi_dir)
        except: pass
    scheduler_process = None
    if os.path.exists(os.path.join(pi_dir, "pi_scheduler.py")):
        try:
            scheduler_process = subprocess.Popen([sys.executable, "pi_scheduler.py"], stdout=open(os.path.join(pi_dir, "scheduler_output.log"), "a", encoding="utf-8"), stderr=open(os.path.join(pi_dir, "scheduler_error.log"), "a", encoding="utf-8"), cwd=pi_dir)
        except: pass
    memory_dir = os.path.join(PI_CONFIG_ROOT, "memory")
    append_system_path = os.path.join(PI_CONFIG_ROOT, "APPEND_SYSTEM.md")
    try:
        if os.path.exists(memory_dir):
            memory_contents = []
            for filename in os.listdir(memory_dir):
                if filename.endswith(".md"):
                    with open(os.path.join(memory_dir, filename), "r", encoding="utf-8") as f:
                        c = f.read().strip()
                        if c: memory_contents.append(f"### Memory: {filename}\n{c}\n")
            if memory_contents:
                with open(append_system_path, "w", encoding="utf-8") as f: f.write("# User Memory / Preferences\n\n" + "\n".join(memory_contents))
    except: pass
    remind_notion_tasks()
    node_cmd = "node"
    cli_js = os.path.join(pi_dir, "packages", "coding-agent", "dist", "cli.js")
    tsx_mjs = os.path.join(pi_dir, "node_modules", "tsx", "dist", "cli.mjs")
    cli_ts = os.path.join(pi_dir, "packages", "coding-agent", "src", "cli.ts")
    launch_cmd = [node_cmd, cli_js] if os.path.exists(cli_js) else [node_cmd, tsx_mjs, cli_ts]
    try:
        subprocess.run(launch_cmd, check=True, cwd=pi_dir)
    except: pass
    finally:
        if linkpi_process: linkpi_process.terminate()
        if scheduler_process: scheduler_process.terminate()
        if meridian_process: meridian_process.terminate()
        remove_meridian_from_models_json()
