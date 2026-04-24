import os
from dotenv import load_dotenv
import httpx

load_dotenv()

class NotionPureCreator:
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

    def create_page_minimal(self, database_id, title, sub_items, target_heading):
        print(f"Starting Minimalist Creation for: {title}")
        
        try:
            # 1. Build blocks
            blocks = []
            # Intro
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
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": target_heading}}]}
            })
            
            # Insert Sub-items
            for item in sub_items:
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": item}}]
                    }
                })
                
            # Heading: Others
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "臨時動議"}}]}
            })

            # 2. Payload (ONLY set the title, skip status to avoid error)
            payload = {
                "parent": {"database_id": database_id},
                "properties": {
                    "名稱": {
                        "title": [{"text": {"content": title}}]
                    }
                },
                "children": blocks
            }

            print("Sending request (skipping status property to ensure success)...")
            response = self.http_client.post(f"{self.base_url}/pages", json=payload)
            
            if response.status_code == 200:
                print(f"SUCCESS: Page '{title}' created perfectly!")
                return True
            else:
                print(f"FAILED: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"ERROR: {e}")
            return False
        finally:
            self.http_client.close()

if __name__ == "__main__":
    DB_ID = "34caad32-6752-8041-9295-fac5ed2ffdee"
    NEW_TITLE = "m20260424_FINAL"
    SUB_ITEMS = ["Chatbot", "tc", "csc", "cs", "ed", "fts"]
    TARGET_H = "本期討論事項"
    
    creator = NotionPureCreator()
    creator.create_page_minimal(DB_ID, NEW_TITLE, SUB_ITEMS, TARGET_H)
