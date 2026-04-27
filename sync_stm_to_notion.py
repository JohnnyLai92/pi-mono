import os
import requests
from datetime import datetime

def sync_to_notion(page_id, stm_content):
    token = os.getenv("NOTION_TOKEN")
    if not token:
        print("Error: NOTION_TOKEN not set.")
        return

    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    # Parse STM content (simplified approach for this task)
    # We will create a heading and then list the items as bullets
    
    blocks = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": f"🤖 STM 自動同步 ({datetime.now().strftime('%Y-%m-%d %H:%M')})"}}]}
        }
    ]

    # Add Key Findings
    blocks.append({
        "object": "block",
        "type": "heading_3",
        "heading_3": {"rich_text": [{"type": "text", "text": {"content": "💡 關鍵發現"}}]}
    })
    
    findings = [
        "遠端倉庫誤將 packages/agent/dist 與 node_modules 納入版控",
        "LTM 檢索曾出現「幻覺」：漏列 CRITICAL_RULES.md 等檔案"
    ]
    
    for finding in findings:
        blocks.append({
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": finding}}]}
        })

    # Add To-Dos
    blocks.append({
        "object": "block",
        "type": "heading_3",
        "heading_3": {"rich_text": [{"type": "text", "text": {"content": "⏳ 待辦事項"}}]}
    })
    
    todos = [
        "評估是否需從遠端倉庫清除已誤提交的 dist 與 node_modules",
        "統一 LTM 檢索 SOP：每次回答前先 ls 一次 .pi/memory/",
        "檢視 CRITICAL_RULES.md 與 preferences.md 中的重複規則"
    ]
    
    for todo in todos:
        blocks.append({
            "object": "block",
            "type": "to_do",
            "to_do": {"rich_text": [{"type": "text", "text": {"content": todo}}], "checked": False}
        })

    response = requests.patch(url, json={"children": blocks}, headers=headers, verify=False)
    if response.status_code == 200:
        print("Success: Synced to Notion!")
    else:
        print(f"Error: {response.status_code}, {response.text}")

if __name__ == "__main__":
    # Extracting ID from the provided URL: 34caad3267528151b6c5fbec3fd53cad
    target_page_id = "34caad3267528151b6c5fbec3fd53cad"
    sync_to_notion(target_page_id, "")
