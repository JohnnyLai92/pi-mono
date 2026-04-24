import os
from dotenv import load_dotenv
import httpx

load_dotenv()

class NotionSmartInitializer:
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

    def initialize_task(self, page_id, target_status_name="Todo"):
        print(f"🚀 Smart Initialization for Page ID: {page_id}")
        
        try:
            # 1. 獲取頁面目前的所有屬性，以確認正確的欄位名稱
            print("🔍 Identifying correct property names...")
            page_res = self.http_client.get(f"{self.base_url}/pages/{page_id}")
            page_res.raise_for_status()
            properties = page_res.json().get("properties", {})
            
            actual_status_key = None
            for p_name, p_info in properties.items():
                # 尋找類型為 select 且名稱包含 'status' 或 '狀態' 的欄位
                normalized_name = p_name.lower().strip()
                if p_info.get("type") == "select" and ("status" in normalized_name or "狀態" in normalized_name):
                    actual_status_key = p_name
                    break
            
            if not actual_status_key:
                print("❌ Could not find a 'Status' property in this page. Available properties are:")
                for k in properties.keys(): print(f"   - {k}")
                return False

            print(f"✅ Found Status property: '{actual_status_key}'")

            # 2. 執行更新
            print(f"🔄 Setting status to '{target_status_name}'...")
            payload = {
                "properties": {
                    actual_status_key: {
                        "select": {"name": target_status_name}
                    }
                }
            }
            
            update_res = self.http_client.patch(f"{self.base_url}/pages/{page_id}", json=payload)
            
            if update_res.status_code == 200:
                print(f"🎉 SUCCESS: Page status updated to '{target_status_name}'!")
                return True
            else:
                print(f"❌ FAILED: {update_res.status_code} - {update_res.text}")
                return False

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False
        finally:
            self.http_client.close()

if __name__ == "__main__":
    TARGET_PAGE_ID = "34caad32-6752-80f5-af7a-d9bf558374dc"
    initializer = NotionSmartInitializer()
    initializer.initialize_task(TARGET_PAGE_ID, "Todo")
