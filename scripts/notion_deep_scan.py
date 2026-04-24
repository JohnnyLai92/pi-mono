import os
from dotenv import load_dotenv
import httpx

load_dotenv()

def deep_scan_notion(title_query):
    token = os.getenv("NOTION_TOKEN")
    base_url = "https://api.notion.com/v1"
    http_client = httpx.Client(headers={"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28"}, verify=False)

    try:
        # 1. Search
        search_res = http_client.post(f"{base_url}/search", json={"query": title_query})
        page_id = search_res.json()["results"][0]["id"]
        
        # 2. Get all blocks
        block_res = http_client.get(f"{base_url}/blocks/{page_id}/children")
        blocks = block_res.json().get("results", [])
        
        target_section = False
        print(f"--- 開始深度掃描 [{title_query}] ---")
        
        for block in blocks:
            b_type = block["type"]
            text = ""
            
            # 提取文字
            if b_type in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "to_do"]:
                try:
                    text = block[b_type]["rich_text"][0]["text"]["content"]
                except: pass
            
            # 偵測標題切換
            if b_type in ["heading_1", "heading_2", "heading_3"]:
                if "上期未完成" in text or "討論項目" in text:
                    target_section = True
                    print(f"\n[進入目標區塊: {text}]")
                else:
                    target_section = False
            
            # 如果在目標區塊內，且有文字，則列出
            if target_section and text:
                print(f"內容: {text}")

    except Exception as e:
        print(f"錯誤: {e}")
    finally:
        http_client.close()

if __name__ == "__main__":
    deep_scan_notion("m20260422")
