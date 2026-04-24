import os
from dotenv import load_dotenv
import httpx

load_dotenv()

def delete_page(page_id):
    token = os.getenv("NOTION_TOKEN")
    base_url = "https://api.notion.com/v1"
    http_client = httpx.Client(
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        },
        verify=False
    )

    try:
        print(f"Attempting to DELETE page ID: {page_id}")
        # Notion API 使用 DELETE 方法來移除頁面
        response = http_client.delete(f"{base_url}/pages/{page_id}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Page deleted successfully!")
            return True
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False
    finally:
        http_client.close()

if __name__ == "__main__":
    # 根據之前的分析，m20260422 的 ID 是 34caad32-6752-80f5-af7a-d9bf558374dc
    TARGET_PAGE_ID = "34caad32-6752-80f5-af7a-d9bf558374dc"
    delete_page(TARGET_PAGE_ID)
