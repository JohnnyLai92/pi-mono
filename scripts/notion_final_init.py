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
        """
        根據偵測到的真實 Schema 進行初始化
        """
        print(f"🚀 Final Initialization for Page ID: {page_id}")
        
        try:
            # 根據 raw_properties_dump.json 的結果：
            # 1. 狀態欄位名稱是 "狀態" (type: status)
            # 2. 標題欄位名稱是 "名稱" (type: title)
            # 3. 負責人欄位名稱是 "Owner" (type: people)

            print(f"Targeting status column: '狀態' (type: status)")
            print(f"Targeting title column: '名稱' (type: title)")

            # Notion Status 類型的更新格式為: {"status": {"name": "..."}}
            # 注意：如果是 status 類型，API 結構是 {"status": {"name": "..."}} 
            # 但在 patch properties 時，如果是 status 類型，通常需要對應其特定的結構
            
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
                print(f"✅ SUCCESS: Status updated to '{status_name}'!")
                return True
            else:
                print(f"❌ FAILED: {response.status_code} - {response.text}")
                # 如果 status 類型報錯，嘗試改用 select 格式 (某些 Notion 版本轉換問題)
                print("Attempting fallback to 'select' type...")
                fallback_payload = {
                    "properties": {
                        "狀態": {
                            "select": {"name": status_name}
                        }
                    }
                }
                response = self.http_client.patch(f"{self.base_url}/pages/{page_id}", json=fallback_payload)
                if response.status_code == 200:
                    print(f"✅ SUCCESS (Fallback): Status updated via 'select'!")
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
    TARGET_PAGE_ID = "34caad32-6752-80f5-af7a-d9bf558374dc"
    initializer = NotionFinalInitializer()
    # 嘗試將狀態改為 "Todo" (請確保 Notion 中 status 選項有這個名稱，或 API 會自動建立)
    initializer.initialize_task_final(TARGET_PAGE_ID, "Todo")
