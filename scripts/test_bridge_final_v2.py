import os
import json

class ClaudeBridge:
    def __init__(self, max_retries=2):
        self.max_retries = max_retries
        self.failure_count = 0
        self.error_history = []
        self.current_task = ""

    def set_task(self, task_description):
        self.current_task = task_description
        print(f"Task context set: {self.current_task}")

    def report_failure(self, error_msg, attempt_details=""):
        self.failure_count += 1
        error_entry = {
            "attempt": self.failure_count,
            "error": error_msg,
            "details": attempt_details
        }
        self.error_history.append(error_entry)
        
        print(f"Failure {self.failure_count}/{self.max_retries} recorded.")
        print(f"   Error: {error_msg}")

        if self.failure_count >= self.max_retries:
            return self.escalate_to_claude()
        return False

    def escalate_to_claude(self):
        print("\n[THRESHOLD REACHED] Escalating to Claude...")
        
        prompt_data = {
            "instruction": "Analyze the following failure history and provide a solution.",
            "task": self.current_task,
            "history": self.error_history
        }
        
        # Simulate Claude Response
        print(f"Sending prompt to Claude: {json.dumps(prompt_data, ensure_ascii=False)}")
        
        print("\n--- CLAUDE RESPONSE ---")
        print("Analysis: The error is caused by a mismatch between the 'status' property type and the provided option.")
        print("Solution: 1. Fetch exact options via GET /databases/{id}. 2. Use the exact string for the 'status' field.")
        print("----------------------\n")
        return "SUCCESS"

if __name__ == "__main__":
    bridge = ClaudeBridge(max_retries=2)
    bridge.set_task("Fixing Notion API Status Property Error")
    
    # Simulate failures
    bridge.report_failure("Error 1: Unicode mismatch", "Tried printing status")
    bridge.report_failure("Error 2: 400 Bad Request", "Tried using wrong status option")
