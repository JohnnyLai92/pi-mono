import os
from dotenv import load_dotenv
import httpx

load_dotenv()

class NotionCompleteRecreator:
    def __init__(self):
        self.token = os.getenv("NOTION_TOKEN")
        self.base_url = "https://api.notion.com/v1"
        self.http_client = httpx.Client(
            headers={
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            },
            verify=False
        )

    def create_perfect_page(self, database_id, title, status="Todo", sub_items=None):
        print(f"Starting operation: Create new page '{title}'")
        
        try:
            # 1. Build the block structure
            blocks = []
            # Intro paragraph
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": "會議紀錄內容預留。"}}]}
            })
            
            # Heading: Last Meeting
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "上次討論事項"}}]}
            })
            
            # Heading: Current Meeting
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "本期討論事項"}}]}
            })
            
            # Insert Sub-items
            if sub_items:
                for item in sub_items:
                    blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": item}}]
                        }
                    })
            
            # Heading: Other
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "臨時動議"}}]}
            })

            # 2. Prepare Page Payload
            payload = {
                "parent": {"database_id": database_id},
                "properties": {
                    "名稱": {
                        "title": [{"text": {"content": title}}]
                    },
                    "狀態": {
                        "status": {"name": status}
                    }
                },
                "children": blocks
            }

            print("Sending request to Notion...")
            response = self.http_client.post(f"{self.base_url}/pages", json=payload)
            
            if response.status_code == 200:
                print(f"SUCCESS: Created page '{title}'")
                return True
            else:
                print(f"FAILED: {response.status_code} - {response.text}")
                # If status fails, try fallback to select
                print("Attempting fallback with 'select' type...")
                payload["properties"]["狀態"] = {"select": {"name": status}}
                response = self.http_client.post(f"{self.base_url}/pages", json=payload)
                if response.status_code == 200:
                    print("SUCCESS (via select fallback)!")
                    return True
                else:
                    print(f"FALLBACK FAILED: {response.text}")
                    return False

        except Exception as e:
            print(f"ERROR: {e}")
            return False
        finally:
            self.http_client.close()

if __name__ == "__main__":
    # Target Database ID from previous steps
    DB_ID = "34caad32-6752-8041-9295-fac5ed2ffdee"
    NEW_TITLE = "m20260424_REBUILT"
    ITEMS = ["Chatbot", "tc", "csc", "cs", "ed", "fts"]
    
    rebuilder = NotionCompleteRecreator()
    rebuilder.create_perfect_page(DB_ID, NEW_TITLE, "Todo", ITEMS)
