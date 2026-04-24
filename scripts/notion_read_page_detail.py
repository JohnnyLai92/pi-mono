import os
from dotenv import load_dotenv
import httpx

load_dotenv()

def read_page_content(page_id):
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
        print(f"Reading content for Page ID: {page_id}\n")
        # 取得該頁面的所有 Blocks
        response = http_client.get(f"{base_url}/blocks/{page_id}/children")
        response.raise_for_status()
        blocks = response.json().get("results", [])
        
        if not blocks:
            print("此頁面沒有任何內容。")
            return

        for block in blocks:
            b_type = block["type"]
            text = ""
            
            # 處理各種 Block 類型的文字內容
            if b_type in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "to_do"]:
                try:
                    rich_text = block[b_type].get("rich_text", [])
                    if rich_text:
                        text = rich_text[0]["text"]["content"]
                except:
                    text = ""
            
            if text:
                # 根據類型加上簡單的前綴
                prefix = f"[{b_type.upper()}]"
                print(f"{prefix} {text}")
            elif b_type == "to_do":
                # 如果是 empty to_do，還是印出一個空行以便識別
                print("[TO-DO] (empty)")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        http_client.close()

if __name__ == "__main__":
    PAGE_ID = "34caad32-6752-80f5-af7a-d9bf558374dc"
    read_page_content(PAGE_ID)
