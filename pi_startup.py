import subprocess
import threading
import time
import os
import datetime
import sys

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

    # 1. 啟動背景 GitHub 同步執行緒
    sync_thread = threading.Thread(target=auto_sync_github, daemon=True)
    sync_thread.start()
    print("[小白報報] 🕒 排程同步服務已啟動 (每小時執行一次)。")

    # 2. 啟動背景 LinkPi 伺服器
    print("[小白報報] 🚀 正在啟動 LinkPi 伺服器 (綁定 0.0.0.0:8765)...")
    try:
        linkpi_process = subprocess.Popen(
            [sys.executable, "LinkPi.py", "--host", "0.0.0.0"],
            stdout=subprocess.DEVNULL, # 隱藏 LinkPi 的日誌輸出，保持畫面乾淨
            stderr=subprocess.DEVNULL,
            cwd=pi_dir
        )
    except Exception as e:
        print(f"[小白報報] ❌ LinkPi 啟動失敗: {e}")
        sys.exit(1)

    # 2.2 啟動背景 pi_scheduler (LineBot 排程中心)
    print("[小白報報] ⏰ 正在啟動 pi_scheduler 排程中心...")
    linebot_dir = os.path.abspath(os.path.join(pi_dir, "..", "..", "LineBot"))
    scheduler_process = None
    if os.path.exists(os.path.join(linebot_dir, "pi_scheduler.py")):
        try:
            scheduler_process = subprocess.Popen(
                [sys.executable, "pi_scheduler.py"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=linebot_dir
            )
            print("[小白報報] ✅ pi_scheduler 已啟動。")
        except Exception as e:
            print(f"[小白報報] ❌ pi_scheduler 啟動失敗: {e}")
    else:
        print(f"[小白報報] ⚠️ 找不到 {os.path.join(linebot_dir, 'pi_scheduler.py')}，跳過啟動。")

    # 2.5 整合記憶區 (從 .pi/memory/*.md 建立 .pi/APPEND_SYSTEM.md)
    memory_dir = os.path.join(pi_dir, ".pi", "memory")
    append_system_path = os.path.join(pi_dir, ".pi", "APPEND_SYSTEM.md")

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
    time.sleep(2) # 等待 LinkPi 啟動一下下

    node_cmd = "node"
    tsx_mjs  = os.path.join(pi_dir, "node_modules", "tsx", "dist", "cli.mjs")
    cli_ts   = os.path.join(pi_dir, "packages", "coding-agent", "src", "cli.ts")

    try:
        subprocess.run([node_cmd, tsx_mjs, cli_ts], check=True, cwd=pi_dir)
    except KeyboardInterrupt:
        # 強尼按下 Ctrl+C 離開
        pass
    except FileNotFoundError:
        print("\n[小白報報] ❌ 找不到 node 指令，請確認 Node.js 是否已安裝並加入環境變數。")
    finally:
        # 當強尼關閉 pi 介面時，把 LinkPi 也關掉
        print("\n[小白報報] 💤 小白準備去睡覺了，正在關閉背景服務...")
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
                
        print("[小白報報] 拜拜強尼！ 👋")
