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

    def create_meeting_page(self, title_text, status_name="Todo", content_text=""):
        print(f"Attempting to create: {title_text}")
        
        try:
            print("Step 1: Identifying correct property names...")
            page_res = self.http_client.get(f"{self.base_url}/pages/{self.database_id}") # 這裡應該是 database，但 get pages 會報錯，我們改用 get database
            # 修正：要獲取 schema 必須用 get database
            page_res = self.http_client.get(f"{self.base_url}/databases/{self.database_id}")
            page_res.raise_for_status()
            props = page_res.json().get("properties", {})
            
            status_col_name = None
            for p_name, p_info in props.items():
                if p_info.get("type") == "status":
                    status_col_name = p_name
                    break
            
            if not status_col_name:
                print("Could not find status column. Using fallback logic.")
                # 如果找不到，嘗試找 select
                for p_name, p_info in props.items():
                    if p_info.get("type") == "select":
                        status_col_name = p_name
                        break

            if not status_col_name:
                print("ERROR: No status or select column found.")
                return False

            print(f"Found column: {status_col_name}")

            print(f"Step 2: Creating page with status '{status_name}'...")
            
            # 構建 payload
            # 我們優先嘗試使用 status 結構，如果失敗則改用 select
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

            response = self.http_client.post(f"{self.base_url}/pages", json=payload)
            
            if response.status_code == 200:
                print("SUCCESS: Page created!")
                return True
            else:
                print(f"FAILED ({response.status_code}): {response.text}")
                if "status" in response.text and "select" in str(payload):
                     # 這邊邏輯有點亂，我們直接做一個萬用的 fallback
                     pass
                
                # 最終暴力 fallback: 改用 select 結構
                print("Trying fallback with 'select' type...")
                fallback_payload = {
                    "parent": {"database_id": self.database_id},
                    "properties": {
                        "名稱": {
                            "title": [{"text": {"content": title_text}}]
                        },
                        status_col_name: {
                            "select": {"name": status_name}
                        }
                    }
                }
                if content_text:
                    fallback_payload["children"] = payload.get("children", [])
                
                response = self.http_client.post(f"{self.base_url}/pages", json=fallback_payload)
                if response.status_code == 200:
                    print("SUCCESS (via select fallback): Page created!")
                    return True
                else:
                    print(f"FALLBACK FAILED: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            print(f"ERROR: {e}")
            return False
        finally:
            self.http_client.close()

if __name__ == "__main__":
    # 注意：這裡的 DATABASE_ID 需要確保正確
    # 我們直接從環境變數讀取
    creator = NotionMeetingCreatorFinal()
    creator.create_meeting_page("m20260424", "Todo", "會議紀錄內容預留。")
