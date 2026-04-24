import os
from dotenv import load_dotenv
import httpx

load_dotenv()

class NotionPropertyManager:
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

    def add_person_property(self, page_id, property_name="Owner"):
        """
        為指定頁面新增一個 'people' 類型的屬性。
        """
        print(f"Adding property: {property_name} (Type: people) to page: {page_id}...")
        
        try:
            # 1. Find the parent database
            page_res = self.http_client.get(f"{self.base_url}/pages/{page_id}")
            page_res.raise_for_status()
            page_data = page_res.json()
            
            database_id = page_data["parent"]["database_id"]
            print(f"Found parent database ID: {database_id}")

            # 2. Update Database Schema to add the new property
            print(f"Modifying database schema to add '{property_name}'...")
            db_payload = {
                "properties": {
                    property_name: {
                        "people": {}
                    }
                }
            }
            db_res = self.http_client.patch(f"{self.base_url}/databases/{database_id}", json=db_payload)
            db_res.raise_for_status()
            print(f"SUCCESS: Property '{property_name}' added to database.")
            
            return True

        except Exception as e:
            print(f"FAILED: {e}")
            return False

if __name__ == "__main__":
    PAGE_ID = "34caad32-6752-80f5-af7a-d9bf558374dc"
    manager = NotionPropertyManager()
    manager.add_person_property(PAGE_ID, "Owner")
