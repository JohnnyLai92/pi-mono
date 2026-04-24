import os
from dotenv import load_dotenv
import httpx

load_dotenv()

class NotionMeetingCreatorFinal:
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
        print(f"Attempting to create: {title_text}")
        
        try:
            # 1. Find the correct property names via schema
            print("Step 1: Fetching database schema...")
            db_res = self.http_client.get(f"{self.base_url}/databases/{self.database_id}")
            db_res.raise_for_status()
            props = db_res.json().get("properties", {})
            
            status_col = None
            valid_status_name = None

            # Find status column and its first available option
            for p_name, p_info in props.items():
                if p_info.get("type") == "status":
                    status_col = p_name
                    options = p_info.get("status", {}).get("options", [])
                    if options:
                        valid_status_name = options[0]["name"]
                    break
            
            if not status_col:
                print("ERROR: Could not find status column.")
                return False

            # Fallback if no options found in schema
            if not valid_status_name:
                valid_status_name = "未開始"

            print(f"Step 2: Identified column '{status_col}' with first option '{valid_status_name}'")

            # 2. Build Payload
            payload = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "名稱": {
                        "title": [{"text": {"content": title_text}}]
                    },
                    status_col: {
                        "status": {"name": valid_status_name}
                    }
                }
            }

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

            # 3. Execute
            print(f"Step 3: Sending POST request...")
            response = self.http_client.post(f"{self.base_url}/pages", json=payload)
            
            if response.status_code == 200:
                print(f"SUCCESS: Meeting page '{title_text}' created with status '{valid_status_name}'!")
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
    creator = NotionMeetingCreatorFinal()
    creator.create_meeting_page("m20260424", "會議紀錄內容預留。")
