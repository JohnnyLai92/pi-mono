import os
from dotenv import load_dotenv
import httpx

load_dotenv()

def verify_encoding(title_query):
    token = os.getenv("NOTION_TOKEN")
    base_url = "https://api.notion.com/v1"
    http_client = httpx.Client(
        headers={"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28"},
        verify=False
    )

    try:
        # 1. 搜尋
        search_res = http_client.post(f"{base_url}/search", json={"query": title_query})
        page_id = search_res.json()["results"][0]["id"]
        
        # 2. 讀取 Blocks
        block_res = http_client.get(f"{base_url}/blocks/{page_id}/children")
        blocks = block_res.json().get("results", [])
        
        # 3. 寫入 UTF-8 檔案
        with open("notion_content_debug.txt", "w", encoding="utf-8") as f:
            for block in blocks:
                b_type = block["type"]
                if b_type in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item"]:
                    try:
                        text = block[b_type]["rich_text"][0]["text"]["content"]
                        f.write(f"{b_type}: {text}\n")
                    except:
                        pass
        print("✅ 驗證完成！請檢查目錄下的 'notion_content_debug.txt' 檔案。")

    except Exception as e:
        print(f"❌ 錯誤: {e}")
    finally:
        http_client.close()

if __name__ == "__main__":
    verify_encoding("m20260422")
