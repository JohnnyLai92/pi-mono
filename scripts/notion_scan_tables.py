import os
from dotenv import load_dotenv
import httpx

load_dotenv()

def scan_tables(title_query):
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

        # 2. 獲取主頁面的所有 Blocks
        block_res = http_client.get(f"{base_url}/blocks/{page_id}/children")
        block_res.raise_for_status()
        blocks = block_res.json().get("results", [])
        
        found_table = False
        for block in blocks:
            # Notion 的表格通常是 collection 或 database 相關的 block
            # 在 blocks 列表裡，database 通常呈現為 'child_database' 類型
            if block["type"] == "child_database":
                found_table = True
                db_id = block["id"]
                db_name = "未知資料庫"
                
                # 嘗試獲取資料庫名稱與 Schema
                db_res = http_client.get(f"{base_url}/databases/{db_id}")
                if db_res.status_code == 200:
                    db_data = db_res.json()
                    # 嘗試獲取標題 (Notion 的 database title 在 properties 裡)
                    # 但通常直接從 database object 的 title 取得
                    # 這裡我們直接抓 properties 來判斷欄位
                    print(f"\n[發現資料庫] ID: {db_id}")
                    
                    properties = db_data.get("properties", {})
                    cols = list(properties.keys())
                    print(f"欄位清單: {cols}")
                    
                    # 3. 查詢資料庫內容 (Query Database)
                    query_res = http_client.post(f"{base_url}/databases/{db_id}/query")
                    query_res.raise_for_status()
                    pages = query_res.json().get("results", [])
                    
                    print(f"共找到 {len(pages)} 筆資料：")
                    print("-" * 30)
                    
                    for p in pages:
                        row_data = {}
                        p_props = p.get("properties", {})
                        for col in cols:
                            prop = p_props.get(col, {})
                            p_type = prop.get("type")
                            
                            val = ""
                            if p_type == "title":
                                val = prop["title"][0]["plain_text"] if prop["title"] else ""
                            elif p_type == "rich_text":
                                val = prop["rich_text"][0]["plain_text"] if prop["rich_text"] else ""
                            elif p_type == "select":
                                val = prop["select"]["name"] if prop["select"] else ""
                            elif p_type == "people":
                                val = prop["people"][0]["name"] if prop["people"] else ""
                            elif p_type == "date":
                                val = prop["date"]["start"] if prop["date"] else ""
                            
                            row_data[col] = val
                        
                        print(f"內容: {row_data}")
                    print("-" * 30)
                else:
                    print(f"無法讀取資料庫詳細資訊: {db_res.status_code}")

        if not found_table:
            print("在此頁面下未發現任何內嵌資料庫 (Inline Database)。")

    except Exception as e:
        print(f"發生錯誤: {e}")
    finally:
        http_client.close()

if __name__ == "__main__":
    scan_tables("m20260422")
