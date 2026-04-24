import os
from dotenv import load_dotenv
import httpx

load_dotenv()

class NotionTaskInitializer:
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

    def initialize_task(self, page_id, status_value, owner_id=None):
        """
        初始化任務：設定狀態與負責人
        """
        print(f"Starting initialization for Page ID: {page_id}...")
        
        try:
            # 1. Prepare payload
            properties_payload = {}

            # Set STATUS (Select type)
            # Note: Notion API handles creating new select options automatically if sent via patch
            properties_payload["STATUS"] = {
                "select": {"name": status_value}
            }

            # Set OWNER (People type)
            if owner_id:
                print(f"Setting Owner ID: {owner_id}")
                properties_payload["Owner"] = {
                    "people": [{"id": owner_id}]
                }
            else:
                print("No Owner ID provided, skipping Owner field.")

            # 2. Send PATCH request
            print(f"Patching properties: {properties_payload}")
            response = self.http_client.patch(
                f"{self.base_url}/pages/{page_id}", 
                json={"properties": properties_payload}
            )
            
            if response.status_code == 200:
                print("SUCCESS: Task initialized successfully!")
                print(f"   - Status set to: {status_value}")
                if owner_id: print(f"   - Owner set to ID: {owner_id}")
                return True
            else:
                print(f"FAILED: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"ERROR: {e}")
            return False

if __name__ == "__main__":
    # Target Page ID
    TARGET_PAGE_ID = "34caad32-6752-80f5-af7a-d9bf558374dc"
    
    # Initialize task with status 'Todo'
    initializer = NotionTaskInitializer()
    initializer.initialize_task(TARGET_PAGE_ID, "Todo")
