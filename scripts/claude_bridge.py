import os
from dotenv import load_dotenv
import subprocess
import json

load_dotenv()

class ClaudeBridge:
    """
    Pi-Claude 協作橋樑。
    當 Pi (本 Agent) 在處理技術問題失敗 2 次後，
    自動封裝上下文並呼叫 Claude 尋求更高階的解決方案。
    """
    def __init__(self, max_retries=2):
        self.max_retries = max_retries
        self.failure_count = 0
        self.error_history = []
        self.current_task = ""

    def set_task(self, task_description):
        """設定目前正在進行的工作任務，以便求助時提供上下文"""
        self.current_task = task_description
        print(f"📝 Task context set: {self.current_task}")

    def report_failure(self, error_msg, attempt_details=""):
        """
        記錄失敗。若達到上限，則自動觸發 Claude 求助。
        """
        self.failure_count += 1
        error_entry = {
            "attempt": self.failure_count,
            "error": error_msg,
            "details": attempt_details
        }
        self.error_history.append(error_entry)
        
        print(f"⚠️ Failure {self.failure_count}/{self.max_retries} recorded.")
        print(f"   Error: {error_msg}")

        if self.failure_count >= self.max_retries:
            return self.escalate_to_claude()
        return False

    def escalate_to_claude(self):
        """
        封裝所有上下文，透過 CLI 呼叫 Claude。
        """
        print("\n🚨 [CRITICAL] Escalating to Claude for expert assistance...")
        
        # 構建精確的 Prompt
        prompt_data = {
            "instruction": "You are an expert senior developer. I am a coding agent (Pi) stuck in a technical loop. Analyze my failure history and provide a direct, implementable solution.",
            "current_task": self.current_task,
            "failure_history": self.error_history,
            "requirement": "Provide code snippets or specific CLI commands to fix the issue. Be concise."
        }
        
        # 為了避免 shell 命令中的引號或編碼問題，我們將 Prompt 寫入臨時檔案
        temp_file = "claude_request.txt"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(json.dumps(prompt_data, ensure_ascii=False, indent=2))

            # 呼叫 claude 指令 (假設支援從檔案讀取或透過 pipe)
            # 我們使用 cat 與 pipe 的方式，這在大多數 shell 環境中最穩定
            print(f"Executing: claude < {temp_file}")
            process = subprocess.Popen(
                ["claude"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8"
            )
            
            with open(temp_file, "r", encoding="utf-8") as f:
                stdout, stderr = process.communicate(input=f.read())

            if process.returncode == 0:
                print("\n✅ Claude's Advice Received:\n")
                print(stdout)
                return stdout
            else:
                print(f"❌ Claude CLI Error: {stderr}")
                return None

        except Exception as e:
            print(f"❌ Failed to communicate with Claude: {e}")
            return None
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def reset(self):
        """成功解決問題後，重置計數器"""
        self.failure_count = 0
        self.error_history = []
        print("🔄 Bridge status reset.")

if __name__ == "__main__":
    # 測試模式
    bridge = ClaudeBridge()
    bridge.set_task("Notion API Integration - Fixing Status Property Error")
    
    # 模擬兩次失敗
    bridge.report_failure("UnicodeEncodeError: 'cp950' codec can't encode...")
    bridge.report_failure("API Error: 400 Bad Request (Invalid status option)")
    
    # 第三次會觸發 escalate
    bridge.report_failure("API Error: 400 (Validation Error)")
