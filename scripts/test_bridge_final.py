import os
import json
import httpx

# 模擬 Claude CLI 的行為，因為環境中可能沒有真實的 claude 指令
class MockClaude:
    def call(self, prompt):
        return """
[Claude's Expert Analysis]
The error occurs because the Notion API is very strict about 'status' type properties.
You cannot use 'select' type for a 'status' column, and you cannot use an option that doesn'
not exist in the schema.

Recommended Solution:
1. Use the 'status' type in your payload.
2. Fetch the exact valid options from the database schema first.
3. Use one of those exact names for the update.

Example Code Snippet:
payload = {
    "properties": {
        "狀態": { "status": { "name": "已完成" } }
    }
}
"""

class ClaudeBridge:
    def __init__(self, max_retries=2):
        self.max_retries = max_retries
        self.failure_count = 0
        self.error_history = []
        self.current_task = ""
        self.mock_mode = True # 開啟模擬模式

    def set_task(self, task_description):
        self.current_task = task_description
        print(f"Task context set: {self.current_task}")

    def report_failure(self, error_msg, attempt_details=""):
        self.failure_count += 1
        self.error_history.append({"attempt": self.failure_count, "error": error_msg, "details": attempt_details})
        print(f"⚠️ Failure {self.failure_count}/{self.max_retries} recorded.")
        if self.failure_count >= self.max_retries:
            return self.escalate_to_claude()
        return False

    def escalate_to_claude(self):
        print("\n🚨 [THRESHOLD REACHED] Escalating to Claude...")
        prompt = {
            "task": self.current_task,
            "errors": self.error_history
        }
        print(f"Sending Prompt to Claude: {json.dumps(prompt, ensure_ascii=False)}")
        
        # 這裡模擬呼叫 claude 指令
        mock = MockClaude()
        response = mock.call(prompt)
        print("\n--- CLAUDE RESPONSE ---")
        print(response)
        return response

if __name__ == "__main__":
    bridge = ClaudeBridge(max_retries=2)
    bridge.set_task("Fixing Notion API Status Property Error")
    
    # 第一次失敗
    bridge.report_failure("Error 1: Unicode mismatch", "Tried printing status")
    
    # 第二次失敗 -> 觸發 Claude
    bridge.report_failure("Error 2: 400 Bad Request", "Tried using wrong status option")
