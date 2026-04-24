import os
from dotenv import load_dotenv
import httpx

load_dotenv()

def search_and_read(query):
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
        print(f"Searching for '{query}'...")
        search_res = http_client.post(f"{base_url}/search", json={"query": query})
        search_res.raise_for_status()
        results = search_res.json().get("results", [])
        
        if not results:
            print("No pages found with that title.")
            return

        # 找到最匹配的頁面
        target_page = None
        for res in results:
            if res["object"] == "page":
                # 嘗試從 properties 提取標題
                props = res.get("properties", {})
                title = ""
                for p_name, p_val in props.items():
                    if p_val.get("type") == "title" and p_val["title"]:
                        title = p_val["title"][0]["plain_text"]
                        break
                if query in title:
                    target_page = res
                    break
        
        if not target_page:
            target_page = results[0] # 如果沒完全匹配，取第一個
            
        page_id = target_page["id"]
        print(f"Found Page ID: {page_id}")

        # 讀取內容
        print("Reading blocks...\n")
        block_res = http_client.get(f"{base_url}/blocks/{page_id}/children")
        block_res.raise_for_status()
        blocks = block_res.json().get("results", [])
        
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
    search_and_read("20240422")
