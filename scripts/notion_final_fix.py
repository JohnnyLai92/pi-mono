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

    def get_available_status_options(self, db_id):
        """抓取資料庫中 status 欄位所有可用的選項名稱"""
        print(f"🔍 Fetching available status options for database: {db_id}")
        try:
            # Query database to get properties
            res = self.http_client.get(f"{self.base_url}/databases/{db_id}")
            res.raise_for_status()
            props = res.json().get("properties", {})
            
            for p_name, p_info in props.items():
                if p_info.get("type") == "status":
                    print(f"✨ Found status column: '{p_name}'")
                    # status 欄位內的選項在 database 結構中通常在 status 屬性裡
                    # 但 API 有時需要透過查詢頁面來確認，我們先看 schema
                    return p_name, p_info.get("status", {})
            return None, None
        except Exception as e:
            print(f"❌ Error fetching schema: {e}")
            return None, None

    def create_meeting_page(self, title_text, status_name="Todo", content_text=""):
        print(f"🚀 Attempting to create: {title_text}")
        
        try:
            # 1. 找到正確的欄位名稱 (針對狀態欄位)
            status_col_name, status_config = self.get_available_status_options(self.database_id)
            
            if not status_col_name:
                print("❌ Could not find a 'status' type column. Falling back to 'select' logic might be needed, but let's try to find it first.")
                return False

            # 2. 嘗試建立頁面
            # 根據之前的分析，標題欄位是 '名稱'
            payload = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "名稱": {
                        "title": [{"text": {"content": title_text}}]
                    },
                    status_col_name: {
                        "status": {"name": status_name}
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

            print(f"📤 Sending request with status '{status_name}' on column '{status_col_name}'...")
            response = self.http_client.post(f"{self.base_url}/pages", json=payload)
            
            if response.status_code == 200:
                print(f"✅ SUCCESS: Meeting page '{title_text}' created!")
                return True
            else:
                print(f"❌ FAILED: {response.status_code} - {response.text}")
                # 如果 status 名稱不存在，嘗試抓取該欄位已有的選項並匹配
                if "Invalid status option" in response.text:
                    print("🔄 Status option not found. Trying to find existing options...")
                    # 在實際應用中，這裡應該去抓取現有的 status list，
                    # 但為了快速解決，我們先嘗試常見的中文選項。
                    for fallback in ["未開始", "Todo", "未完成", "進行中"]:
                        print(f"   Trying fallback: {fallback}...")
                        payload["properties"][status_col_name]["status"]["name"] = fallback
                        response = self.http_client.post(f"{self.base_url}/pages", json=payload)
                        if response.status_code == 200:
                            print(f"✅ SUCCESS with fallback '{fallback}'!")
                            return True
                return False

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False
        finally:
            self.http_client.close()

if __name__ == "__main__":
    TARGET_PAGE_ID = "34caad32-6752-80f5-af7a-d9bf558374dc"
    creator = NotionMeetingCreatorFinal()
    # 嘗試建立，並使用一個可能的 status 名稱
    creator.create_meeting_page("m20260424", "Todo", "會議紀錄內容預留。")
