import os
from dotenv import load_dotenv
import httpx
from datetime import datetime

load_dotenv()

class NotionMeetingCreator:
    def __init__(self):
        self.token = os.getenv("NOTION_TOKEN")
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        self.base_url = "https://api.notion.com/v1"
        self.http_client = httpx.Client(
            headers={
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            },
            verify=False
        )

    def create_meeting_page(self, title_text, content_text=""):
        print(f"🚀 Attempting to create new meeting page: {title_text}")
        
        try:
            # 1. Identify the correct property names from previous analysis
            # Based on our dump: 
            # Title is '名稱'
            # Status is '狀態'
            # Owner is 'Owner'
            
            payload = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "名稱": {
                        "title": [{"text": {"content": title_text}}]
                    },
                    "狀態": {
                        "status": {"name": "Todo"} # Try to use a standard status name
                    }
                }
            }
            
            # Add content as blocks
            if content_text:
                blocks = []
                for line in content_text.strip().split('\n'):
                    if line.strip():
                        blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {"rich_text": [{"type": "text", "text": {"content": line.strip()}}]}
                        })
                payload["children"] = blocks

            print(f"Sending request to create page...")
            response = self.http_client.post(f"{self.base_url}/pages", json=payload)
            
            if response.status_code == 200:
                print(f"✅ SUCCESS: Meeting page '{title_text}' created!")
                print(f"Page ID: {response.json()['id']}")
                return True
            else:
                print(f"❌ FAILED: {response.status_code} - {response.text}")
                # Fallback: If 'status' type fails because "Todo" doesn't exist, try 'select'
                print("Trying fallback with 'select' type for status...")
                fallback_payload = {
                    "parent": {"database_id": self.database_id},
                    "properties": {
                        "名稱": {
                            "title": [{"text": {"content": title_text}}]
                        },
                        "狀態": {
                            "select": {"name": "Todo"}
                        }
                    }
                }
                if content_text:
                    fallback_payload["children"] = payload.get("children", [])
                    
                response = self.http_client.post(f"{self.base_url}/pages", json=fallback_payload)
                if response.status_code == 200:
                    print(f"✅ SUCCESS (Fallback): Meeting page '{title_text}' created using 'select' type!")
                    return True
                else:
                    print(f"❌ FALLBACK FAILED: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False
        finally:
            self.http_client.close()

if __name__ == "__main__":
    creator = NotionMeetingCreator()
    creator.create_meeting_page("m20260424", "會議紀錄內容預留。")
