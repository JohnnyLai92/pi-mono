import os
from dotenv import load_dotenv
import httpx

load_dotenv()

class NotionDeleter:
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

    def delete_page(self, page_id):
        print(f"Attempting to DELETE page ID: {page_id}")
        
        try:
            # 1. Verify existence
            print("Step 1: Verifying page existence...")
            check_res = self.http_client.get(f"{self.base_url}/pages/{page_id}")
            if check_res.status_code != 200:
                print(f"Page not found or error: {check_res.status_code}")
                return False
            print("Page exists. Proceeding...")

            # 2. Execute delete
            print("Step 2: Sending DELETE request...")
            response = self.http_client.delete(f"{self.base_url}/pages/{page_id}")
            
            if response.status_code == 200:
                print("SUCCESS: Page deleted!")
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
    TARGET_PAGE_ID = "34caad32-6752-80f5-af7a-d9bf558374dc"
    deleter = NotionDeleter()
    deleter.delete_page(TARGET_PAGE_ID)
