import os
from dotenv import load_dotenv
import httpx

load_dotenv()

def read_page_content_by_id(page_id):
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
        # 1. Fetch blocks
        response = http_client.get(f"{base_url}/blocks/{page_id}/children")
        response.raise_for_status()
        blocks = response.json().get("results", [])
        
        if not blocks:
            print("No content blocks found.")
            return

        for block in blocks:
            b_type = block["type"]
            text = ""
            
            # Handle different block types
            if b_type in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "to_do"]:
                try:
                    text = block[b_type]["rich_text"][0]["text"]["content"]
                except (IndexError, KeyError):
                    text = ""
            
            if text.strip():
                print(f"[{b_type}] {text}")
            elif b_type == "to_do":
                # For empty to-do items
                print(f"[to_do] (empty)")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        http_client.close()

if __name__ == "__main__":
    # The ID for m20260424 from previous successful creation
    TARGET_PAGE_ID = "34caad32-6752-8148-a6e8-cb4f5311886d"
    read_page_content_by_id(TARGET_PAGE_ID)
