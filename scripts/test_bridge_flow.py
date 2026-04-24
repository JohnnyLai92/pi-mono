import os
from dotenv import load_dotenv
from scripts.claude_bridge import ClaudeBridge

def run_simulation():
    # 初始化橋樑
    bridge = ClaudeBridge(max_retries=2)
    
    # 設定當前任務上下文
    current_task = "Fixing Notion API Status Property Error (Type mismatch: status vs select)"
    bridge.set_task(current_task)
    
    print("\n--- [SIMULATION START] ---")
    
    # 第一次失敗：模擬編碼問題
    print("\n[Attempt 1] Trying to update property via 'select' type...")
    error_1 = "UnicodeEncodeError: 'cp950' codec can't encode character '\u274c'"
    bridge.report_failure(error_1, "Tried using 'select' type for status column, but encoding failed during print.")
    
    print("\n" + "="*30 + "\n")
    
    # 第二次失敗：模擬 API 驗證錯誤
    print("[Attempt 2] Trying to update property via 'status' type with wrong option...")
    error_2 = "400 Bad Request: Invalid status option 'Todo' (Notion expects exact match)"
    bridge.report_failure(error_2, "Tried using 'status' type with 'Todo' option, but API rejected it.")
    
    print("\n--- [SIMULATION END] ---")
    print("If the above worked, the bridge should have triggered 'Escalating to Claude' automatically.")

if __name__ == "__main__":
    run_simulation()
