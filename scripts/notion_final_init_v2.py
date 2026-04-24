import os
from dotenv import load_dotenv
import httpx

load_dotenv()

class NotionFinalInitializer:
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

    def initialize_task_final(self, page_id, status_name="Todo"):
        print(f"Starting Final Initialization for Page ID: {page_id}")
        
        try:
            # Based on raw dump analysis:
            # 1. The status column name is '狀態'
            # 2. The status type is 'status'
            # 3. The title column name is '名稱'
            
            print(f"Targeting status column: '狀態' (type: status)")
            print(f"Targeting title column: '名稱' (type: title)")

            payload = {
                "properties": {
                    "狀態": {
                        "status": {"name": status_name}
                    }
                }
            }

            print(f"Sending payload: {payload}")
            response = self.http_client.patch(f"{self.base_url}/pages/{page_id}", json=payload)
            
            if response.status_code == 200:
                print(f"SUCCESS: Page status updated to '{status_name}'!")
                return True
            else:
                print(f"FAILED: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"ERROR: {e}")
            return False

if __name__ == "__main__":
    TARGET_PAGE_ID = "34caad32-6752-80f5-af7a-d9bf558374dc"
    initializer = NotionFinalInitializer()
    # Use 'Todo' as target status
    initializer.initialize_task_final(TARGET_PAGE_ID, "Todo")
