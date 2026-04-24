import os
from dotenv import load_dotenv
import httpx

load_dotenv()

def recreate_page_from_scratch(database_id, title, sub_items, target_heading):
    token = os.getenv("NOTION_TOKEN")
    base_url = "https://api.notion.com/v1"
    http_client = httpx.Client(
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        },
        verify=False
    )

    try:
        print(f"🚀 Recreating page from scratch: {title}")
        
        # 1. 定義全新的 Blocks 結構
        # 為了確保完全正確，我們直接定義好所有需要的 Blocks
        new_blocks = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": "會議紀錄內容預留。"}}]}
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "上次討論事項"}}]}
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": target_heading}}]}
            }
        ]
        
        # 插入子項目
        for item in sub_items:
            new_blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": item}}]
                }
            })
            
        new_blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "臨時動議"}}]}
        })

        # 2. 建立新頁面
        print("Step 2: Creating new page in database...")
        payload = {
            "parent": {"database_id": database_id},
            "properties": {
                "名稱": {
                    "title": [{"text": {"content": title}}]
                },
                "狀態": {
                    "status": {"name": "Todo"}
                }
            },
            "children": new_blocks
        }
        
        response = http_client.post(f"{base_url}/pages", json=payload)
        
        if response.status_code == 200:
            print(f"✅ SUCCESS: New page '{title}' created with perfect structure!")
            return True
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False
    finally:
        http_client.close()

if __name__ == "__main__":
    # 使用原本的資料庫 ID
    DB_ID = "34caad32-6752-8041-9295-fac5ed2ffdee"
    NEW_TITLE = "m20260424_REBUILT"
    SUB_ITEMS = ["Chatbot", "tc", "csc", "cs", "ed", "fts"]
    TARGET_H = "本期討論事項"
    
    recreate_page_from_scratch(DB_ID, NEW_TITLE, SUB_ITEMS, TARGET_H)
