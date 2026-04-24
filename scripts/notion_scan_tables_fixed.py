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
        search_res = http_client.post(f"{base_url}/search", json={"query": title_query})
        search_res.raise_for_status()
        results = search_res.json().get("results", [])
        if not results:
            print("找不到主頁面")
            return
        
        page_id = results[0]["id"]
        block_res = http_client.get(f"{base_url}/blocks/{page_id}/children")
        block_res.raise_for_status()
        blocks = block_res.json().get("results", [])
        
        for block in blocks:
            if block["type"] == "child_database":
                db_id = block["id"]
                db_res = http_client.get(f"{base_url}/databases/{db_id}")
                db_res.raise_for_status()
                db_data = db_res.json()
                
                properties = db_data.get("properties", {})
                cols = list(properties.keys())
                
                print(f"\n[發現資料庫] ID: {db_id}")
                print(f"欄位清單: {cols}")
                
                query_res = http_client.post(f"{base_url}/databases/{db_id}/query")
                query_res.raise_for_status()
                pages = query_res.json().get("results", [])
                
                print(f"找到 {len(pages)} 筆紀錄：")
                print("-" * 50)
                for p in pages:
                    row = {}
                    p_props = p.get("properties", {})
                    for col in cols:
                        prop = p_props.get(col, {})
                        p_type = prop.get("type")
                        if p_type == "title" and prop["title"]:
                            row[col] = prop["title"][0]["plain_text"]
                        elif p_type == "rich_text" and prop["rich_text"]:
                            row[col] = prop["rich_text"][0]["plain_text"]
                        elif p_type == "select" and prop["select"]:
                            row[col] = prop["select"]["name"]
                        elif p_type == "people" and prop["people"]:
                            row[col] = prop["people"][0]["name"]
                        else:
                            row[col] = ""
                    print(row)
                print("-" * 50)
                return

        print("未發現內嵌資料庫。")

    except Exception as e:
        print(f"錯誤: {e}")
    finally:
        http_client.close()

if __name__ == "__main__":
    scan_tables("m20260422")
