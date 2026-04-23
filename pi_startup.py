import subprocess
import threading
import time
import os
import datetime
import sys
import json

# 設定 Agent 目錄環境變數
# 優先使用家目錄下的配置，確保跨平台一致性
PI_CONFIG_ROOT = os.path.expanduser("~/.pi")
AGENT_DIR = os.path.join(PI_CONFIG_ROOT, "agent")
os.environ["PI_CODING_AGENT_DIR"] = AGENT_DIR
USER_MODELS_JSON = os.path.join(PI_CONFIG_ROOT, "agent", "models.json")
PROJECT_MODELS_JSON = os.path.join(os.path.dirname(__file__), "packages", "pods", "models.json")

# 決定優先使用的 models.json 路徑
if os.path.exists(USER_MODELS_JSON):
    MODELS_JSON_PATH = USER_MODELS_JSON
    MODELS_SOURCE = f"使用者設定 ({USER_MODELS_JSON})"
else:
    MODELS_JSON_PATH = PROJECT_MODELS_JSON
    MODELS_SOURCE = f"專案內建 ({PROJECT_MODELS_JSON})"

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
        print("[小白報報] 📝 已將 Meridian (localhost:3456) 加入 models.json。")
    except Exception as e:
        print(f"[小白報報] ⚠️ 更新 models.json 失敗: {e}")

def remove_meridian_from_models_json():
    try:
        with open(MODELS_JSON_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        if config.get("providers", {}).pop("meridian", None) is not None:
            with open(MODELS_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def memory_summary_scheduler():
    while True:
        now = datetime.datetime.now()
        # 每天 17:00 觸發
        if now.hour == 17 and now.minute == 0:
            print("\n[小白報報] ⏰ 時間到了！現在是 17:00，是否需要我彙整今日的短期記憶並整理至長期記憶區？")
            # 為了防止在一分鐘內重複觸發，睡眠 61 秒
            time.sleep(61)
        time.sleep(30) # 每 30 秒檢查一次時間

def auto_sync_github():
    while True:
        # 每 3600 秒 (1 小時) 執行一次
        time.sleep(3600)
        print("\n[小白報報] 🔄 正在自動同步 GitHub...")
        try:
            # 檢查是否有變更
            repo_dir = os.path.dirname(os.path.abspath(__file__))
            status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=repo_dir)
            if status.stdout.strip():
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                subprocess.run(["git", "add", "."], check=True, cwd=repo_dir)
                subprocess.run(["git", "commit", "-m", f"Auto-sync: {now}"], check=True, cwd=repo_dir)
                subprocess.run(["git", "push", "origin", "main"], check=True, cwd=repo_dir)
                print(f"[小白報報] ✅ GitHub 同步完成 ({now})")
            else:
                print(f"[小白報報] 📝 專案沒有變更，跳過同步。({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        except Exception as e:
            print(f"\n[小白報報] ❌ GitHub 同步失敗: {e}")

if __name__ == "__main__":
    print("[小白報報] 🐶 總司令腳本啟動！準備就緒...")

    pi_dir = os.path.dirname(os.path.abspath(__file__))

    # 0. 詢問是否啟動 Meridian proxy
    meridian_process = None
    try:
        answer = input("[小白報報] 🔌 是否啟動 Meridian proxy？(y/N) ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        answer = "n"

    if answer == "y":
        # 不論 meridian 是否成功啟動，先寫入 models.json 讓 /model 選單可見
        add_meridian_to_models_json()
        meridian_env = {
            **os.environ,
            "CLAUDE_CONFIG_DIR": os.path.expanduser("~/.config/meridian"),
            "MERIDIAN_DEFAULT_AGENT": "pi",
            "CLAUDE_PROXY_PASSTHROUGH": "true",
        }
        try:
            meridian_process = subprocess.Popen(
                ["meridian"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=meridian_env,
            )
            print("[小白報報] ✅ Meridian proxy 已啟動 (port 3456)，CLAUDE_CONFIG_DIR 獨立隔離。")
        except FileNotFoundError:
            print("[小白報報] ⚠️ 找不到 meridian 指令，請先執行 npm install -g @rynfar/meridian")
            print("[小白報報] 📌 模型選單已加入 Meridian，待安裝後即可使用。")
        except Exception as e:
            print(f"[小白報報] ⚠️ Meridian 啟動失敗（非致命）: {e}")
    else:
        print("[小白報報] ⏭️ 跳過 Meridian。")

    # 1. 啟動背景 GitHub 同步執行緒
    sync_thread = threading.Thread(target=auto_sync_github, daemon=True)
    sync_thread.start()
    print("[小白報報] 🕒 排程同步服務已啟動 (每小時執行一次)。")

    # 1.1 啟動背景記憶彙整提醒執行緒
    mem_thread = threading.Thread(target=memory_summary_scheduler, daemon=True)
    mem_thread.start()
    print("[小白報報] 🧠 記憶彙整排程已啟動 (每日 17:00 提醒)。")

    # 2. 詢問是否啟動 LinkPi 伺服器
    linkpi_process = None
    try:
        linkpi_answer = input("[小白報報] 🔌 是否啟動 LinkPi 伺服器 (port 8765)？(y/N) ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        linkpi_answer = "n"

    if linkpi_answer == "y":
        print("[小白報報] 🚀 正在啟動 LinkPi 伺服器 (綁定 0.0.0.0:8765)...")
        try:
            linkpi_process = subprocess.Popen(
                [sys.executable, "LinkPi.py", "--host", "0.0.0.0"],
                stdout=subprocess.DEVNULL,  # 隱藏 LinkPi 的日誌輸出，保持畫面乾淨
                stderr=subprocess.DEVNULL,
                cwd=pi_dir
            )
            print("[小白報報] ✅ LinkPi 伺服器已啟動 (port 8765)。")
        except Exception as e:
            print(f"[小白報報] ❌ LinkPi 啟動失敗: {e}")
    else:
        print("[小白報報] ⏭️ 跳過 LinkPi。")

    # 2.2 啟動背景 pi_scheduler (LineBot 排程中心)
    print("[小白報報] ⏰ 正在啟動 pi_scheduler 排程中心...")
    linebot_dir = pi_dir
    scheduler_process = None
    if os.path.exists(os.path.join(linebot_dir, "pi_scheduler.py")):
        try:
            # 定義錯誤日誌路徑
            error_log_path = os.path.join(linebot_dir, "scheduler_error.log")
            
            scheduler_process = subprocess.Popen(
                [sys.executable, "pi_scheduler.py"],
                stdout=open(os.path.join(linebot_dir, "scheduler_output.log"), "a", encoding="utf-8"),
                stderr=open(error_log_path, "a", encoding="utf-8"),
                cwd=linebot_dir
            )
            print(f"[小白報報] ✅ pi_scheduler 已啟動。錯誤日誌：{error_log_path}")
        except Exception as e:
            print(f"[小白報報] ❌ pi_scheduler 啟動失敗: {e}")

    else:
        print(f"[小白報報] ⚠️ 找不到 {os.path.join(linebot_dir, 'pi_scheduler.py')}，跳過啟動。")

    # 2.5 整合記憶區 (從 .pi/memory/*.md 建立 .pi/APPEND_SYSTEM.md)
    memory_dir = os.path.join(PI_CONFIG_ROOT, "memory")
    append_system_path = os.path.join(PI_CONFIG_ROOT, "APPEND_SYSTEM.md")

    print("[小白報報] 🧠 正在讀取並整合記憶區...")
    try:
        if os.path.exists(memory_dir):
            memory_contents = []
            for filename in os.listdir(memory_dir):
                if filename.endswith(".md"):
                    filepath = os.path.join(memory_dir, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            memory_contents.append(f"### Memory: {filename}\n{content}\n")
            
            if memory_contents:
                with open(append_system_path, "w", encoding="utf-8") as f:
                    f.write("# User Memory / Preferences\n\n")
                    f.write("\n".join(memory_contents))
                print(f"[小白報報] 💾 成功載入 {len(memory_contents)} 筆記憶！")
            else:
                # 記憶區為空，若舊的 APPEND_SYSTEM.md 存在則刪除，避免載入舊資料
                if os.path.exists(append_system_path):
                    os.remove(append_system_path)
                print("[小白報報] 💭 記憶區目前沒有資料。")
        else:
            print("[小白報報] 💭 找不到記憶區目錄。")
    except Exception as e:
        print(f"[小白報報] ❌ 讀取記憶區失敗: {e}")

    # 3. 在前景喚醒小白 (直接呼叫 node，避免透過 pi.cmd 造成無限循環)
    print("[小白報報] 🐶 正在喚醒小白...")
    time.sleep(0.5) # 等待 LinkPi 啟動一下下

    node_cmd = "node"
    # 優先使用預先編譯的 dist/cli.js（啟動快數倍），若不存在則退回 tsx 即時編譯
    cli_js   = os.path.join(pi_dir, "packages", "coding-agent", "dist", "cli.js")
    tsx_mjs  = os.path.join(pi_dir, "node_modules", "tsx", "dist", "cli.mjs")
    cli_ts   = os.path.join(pi_dir, "packages", "coding-agent", "src", "cli.ts")

    if os.path.exists(cli_js):
        launch_cmd = [node_cmd, cli_js]
        print("[小白報報] ⚡ 使用預編譯版本，啟動加速中...")
    else:
        launch_cmd = [node_cmd, tsx_mjs, cli_ts]
        print("[小白報報] 🔧 使用 tsx 即時編譯（可執行 npm run build 加速後續啟動）")

    try:
        subprocess.run(launch_cmd, check=True, cwd=pi_dir)
    except KeyboardInterrupt:
        # 強尼按下 Ctrl+C 離開
        pass
    except FileNotFoundError:
        print("\n[小白報報] ❌ 找不到 node 指令，請確認 Node.js 是否已安裝並加入環境變數。")
    finally:
        # 當強尼關閉 pi 介面時，把 LinkPi 也關掉
        print("\n[小白報報] 💤 小白準備去睡覺了，正在關閉背景服務...")
        if linkpi_process:
            linkpi_process.terminate()
            try:
                linkpi_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                linkpi_process.kill()
            
        if scheduler_process:
            scheduler_process.terminate()
            try:
                scheduler_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                scheduler_process.kill()

        if answer == "y":
            if meridian_process:
                meridian_process.terminate()
                try:
                    meridian_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    meridian_process.kill()
            remove_meridian_from_models_json()

        print("[小白報報] 拜拜強尼！ 👋")
