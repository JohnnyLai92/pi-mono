import os
import logging
from dotenv import load_dotenv
import httpx

load_dotenv()

def read_notion_page_by_title(title_query):
    token = os.getenv("NOTION_TOKEN")
    # 注意：搜尋功能需要使用 search API
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
        # 1. 使用 Search API 尋找匹配標題的頁面
        search_payload = {"query": title_query, "filter": {"property": "object", "value": "page"}}
        response = http_client.post(f"{base_url}/search", json=search_payload)
        response.raise_for_status()
        
        results = response.json().get("results", [])
        if not results:
            print(f"No page found with query: {title_query}")
            return

        # 假設找到第一個最匹配的
        page = results[0]
        page_id = page["id"]
        print(f"Found page: {title_query} (ID: {page_id})")

        # 2. 讀取該頁面的 Blocks
        block_response = http_client.get(f"{base_url}/blocks/{page_id}/children")
        block_response.raise_for_status()
        
        blocks = block_response.json().get("results", [])
        print("\n--- Page Content ---")
        for block in blocks:
            b_type = block["type"]
            if b_type == "paragraph":
                text = block["paragraph"]["rich_text"][0]["text"]["content"] if block["paragraph"]["rich_text"] else ""
                print(f"[Para] {text}")
            elif b_type == "heading_1":
                text = block["heading_1"]["rich_text"][0]["text"]["content"] if block["heading_1"]["rich_text"] else ""
                print(f"[H1] {text}")
            elif b_type == "heading_2":
                text = block["heading_2"]["rich_text"][0]["text"]["content"] if block["heading_2"]["rich_text"] else ""
                print(f"[H2] {text}")
            elif b_type == "bulleted_list_item":
                text = block["bulleted_list_item"]["rich_text"][0]["text"]["content"] if block["bulleted_list_item"]["rich_text"] else ""
                print(f"[Bullet] {text}")
            elif b_type == "heading_3":
                text = block["heading_3"]["rich_text"][0]["text"]["content"] if block["heading_3"]["rich_text"] else ""
                print(f"[H3] {text}")
        print("--------------------\n")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "m20260422"
    read_notion_page_by_title(query)
