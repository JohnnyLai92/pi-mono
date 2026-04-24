import os
from dotenv import load_dotenv
import httpx

load_dotenv()

def scan_subpages(title_query):
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
        # 1. 搜尋主頁面
        search_res = http_client.post(f"{base_url}/search", json={"query": title_query})
        search_res.raise_for_status()
        results = search_res.json().get("results", [])
        if not results:
            print("找不到主頁面")
            return
        
        page_id = results[0]["id"]
        print(f"找到主頁面 ID: {page_id}")

        # 2. 獲取主頁面的所有 Blocks (包含子頁面)
        block_res = http_client.get(f"{base_url}/blocks/{page_id}/children")
        block_res.raise_for_status()
        blocks = block_res.json().get("results", [])
        
        subpages = []
        for block in blocks:
            if block["type"] == "child_page":
                # 嘗試獲取子頁面的標題
                # 注意：child_page block 本身不直接包含 title，需透過標題屬性或再次調用
                # 但通常在 children 列表中，我們可以從 block 的內容判斷
                # 在 Notion API 中，child_page block 確實很簡略，我們直接紀錄 ID
                subpages.append(block["id"])
        
        if not subpages:
            print("在此頁面下未發現任何子頁面 (Child Pages)。")
            return

        print(f"發現 {len(subpages)} 個子頁面，正在嘗試讀取內容...\n")

        for sid in subpages:
            # 取得子頁面資訊
            page_info_res = http_client.get(f"{base_url}/pages/{sid}")
            page_info_res.raise_for_status()
            page_data = page_info_res.json()
            
            # 獲取頁面標題
            title = ""
            try:
                title = page_data["properties"]["Name"]["title"][0]["text"]["content"]
            except:
                try:
                    title = page_data["properties"]["title"]["title"][0]["text"]["content"]
                except:
                    title = "未知標題"

            print(f"--- 子頁面: {title} ---")
            
            # 讀取子頁面內容
            content_res = http_client.get(f"{base_url}/blocks/{sid}/children")
            content_res.raise_for_status()
            c_blocks = content_res.json().get("results", [])
            
            for cb in c_blocks:
                bt = cb["type"]
                ctext = ""
                if bt in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "to_do"]:
                    try:
                        ctext = cb[bt]["rich_text"][0]["text"]["content"]
                    except: pass
                
                if ctext:
                    # 檢查是否包含待辦事項關鍵字
                    status = ""
                    if bt == "to_do":
                        status = "[ ]" if not cb["to_do"].get("checked") else "[x]"
                    print(f"{status} {ctext}")
            print()

    except Exception as e:
        print(f"發生錯誤: {e}")
    finally:
        http_client.close()

if __name__ == "__main__":
    scan_subpages("m20260422")
