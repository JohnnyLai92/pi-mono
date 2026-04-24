import os
from dotenv import load_dotenv
import httpx

load_dotenv()

class NotionContentUpdater:
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

    def add_headings(self, page_id, headings):
        print(f"🚀 Adding headings to Page ID: {page_id}")
        
        # 準備要新增的 blocks
        blocks = []
        for text in headings:
            blocks.append({
                "object": "block",
                "type": "heading_2",  # 使用 H2 作為大標題
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": text}}]
                }
            })

        try:
            print(f"Sending {len(blocks)} heading blocks...")
            payload = {"children": blocks}
            response = self.http_client.patch(
                f"{self.base_url}/blocks/{page_id}/children",
                json=payload
            )
            
            if response.status_code == 200:
                print("✅ SUCCESS: Headings added successfully!")
                return True
            else:
                print(f"❌ FAILED: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False
        finally:
            self.http_client.close()

if __name__ == "__main__":
    # 目標頁面 ID (m20260424)
    TARGET_PAGE_ID = "34caad32-6752-8148-a6e8-cb4f5311886d"
    
    # 定義要新增的標題
    NEW_HEADINGS = ["上次討論事項", "本期討論事項", "臨時動議"]
    
    updater = NotionClass() # 這裡修正 class 名稱
    # 重新定義正確的 class name 呼叫
    from scripts.notion_final_fix_v4 import NotionSyncManager # 其實我們可以直接寫在裡面
    
    # 為了避免 import 錯誤，我們直接重新實作邏輯
    updater = NotionContentUpdater()
    updater.add_headings(TARGET_PAGE_ID, NEW_HEADINGS)
