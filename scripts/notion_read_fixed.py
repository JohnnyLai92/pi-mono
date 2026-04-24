import os
import logging
from dotenv import load_dotenv
import httpx

load_dotenv()

def read_notion_page_by_title(title_query):
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
        # 1. 搜尋頁面
        search_payload = {"query": title_query, "filter": {"property": "object", "value": "page"}}
        response = http_client.post(f"{base_url}/search", json=search_payload)
        response.raise_for_status()
        
        results = response.json().get("results", [])
        if not results:
            print(f"未找到標題包含 '{title_query}' 的頁面")
            return

        page = results[0]
        page_id = page["id"]
        print(f"找到頁面: {title_query} (ID: {page_id})")

        # 2. 讀取 Blocks
        block_response = http_client.get(f"{base_url}/blocks/{page_id}/children")
        block_response.raise_for_status()
        
        blocks = block_response.json().get("results", [])
        print("\n--- 頁面內容 (嘗試 UTF-8 解碼) ---")
        
        for block in blocks:
            b_type = block["type"]
            content = ""
            
            # 提取文字內容
            if b_type in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item"]:
                try:
                    rich_text = block[b_type].get("rich_text", [])
                    if rich_text:
                        content = rich_text[0]["text"]["content"]
                except (KeyError, IndexError):
                    content = ""

            if content:
                # 根據 block 類型顯示
                prefix = f"[{b_type.upper()}]"
                print(f"{prefix} {content}")
        
        print("----------------------------------\n")

    except Exception as e:
        print(f"發生錯誤: {e}")
    finally:
        http_client.close()

if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "m20260422"
    read_notion_page_by_title(query)
