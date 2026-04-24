import os
from dotenv import load_dotenv
import httpx

load_dotenv()

class NotionHeadingManager:
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
        
        try:
            # 準備要新增的 blocks (使用 heading_2 作為大標題)
            blocks = []
            for text in headings:
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": text}}]
                    }
                })

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
    # 剛剛建立的 m20260424 的 ID
    TARGET_PAGE_ID = "34caad32-6752-8148-a6e8-cb4f5311886d"
    
    # 定義標題內容
    NEW_HEADINGS = ["上次討論事項", "本期討論事項", "臨時動議"]
    
    manager = NotionHeadingManager()
    manager.add_headings(TARGET_PAGE_ID, NEW_HEADINGS)
