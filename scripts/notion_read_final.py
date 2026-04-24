import os
from dotenv import load_dotenv
import httpx

load_dotenv()

def read_page(page_id):
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
        print(f"Reading Page ID: {page_id}\n")
        res = http_client.get(f"{base_url}/blocks/{page_id}/children")
        res.raise_for_status()
        blocks = res.json().get("results", [])
        
        if not blocks:
            print("No content blocks found.")
            return

        for block in blocks:
            b_type = block["type"]
            text = ""
            if b_type in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "to_do"]:
                try:
                    text = block[b_type]["rich_text"][0]["text"]["content"]
                except: pass
            
            if text.strip():
                print(f"[{b_type}] {text}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        http_client.close()

if __name__ == "__main__":
    # 使用使用者提到的 m20260422 (假設是輸入錯誤)
    read_page("34caad32-6752-80f5-af7a-d9bf558374dc")
