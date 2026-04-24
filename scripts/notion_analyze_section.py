import os
from dotenv import load_dotenv
import httpx

load_dotenv()

def analyze_section(page_id, target_header):
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
        print(f"Analyzing section [{target_header}] in page {page_id}...\n")
        response = http_client.get(f"{base_url}/blocks/{page_id}/children")
        response.raise_for_status()
        blocks = response.json().get("results", [])
        
        in_target_section = False
        content_found = []
        databases_found = []

        for block in blocks:
            b_type = block["type"]
            
            if b_type in ["heading_1", "heading_2", "heading_3"]:
                try:
                    text = block[b_type]["rich_text"][0]["text"]["content"]
                except:
                    text = ""
                
                if target_header in text:
                    in_target_section = True
                    continue
                elif in_target_section:
                    in_target_section = False

            if in_target_section:
                if b_type == "child_database":
                    databases_found.append(block["id"])
                    continue

                text = ""
                if b_type in ["paragraph", "bulleted_list_item", "to_do"]:
                    try:
                        text = block[b_type]["rich_text"][0]["text"]["content"]
                    except: pass
                
                if text:
                    content_found.append({"type": b_type, "text": text})

        if not content_found and not databases_found:
            print("No content or databases found under this header.")
            return

        if content_found:
            print("📝 Text Content found:")
            for item in content_found:
                print(f" - [{item['type']}] {item['text']}")
        
        if databases_found:
            print(f"\n📊 Found {len(databases_found)} Inline Database(s)!")
            for idx, db_id in enumerate(databases_found):
                print(f"   [{idx+1}] Database ID: {db_id}")
                db_res = http_client.get(f"{base_url}/databases/{db_id}")
                if db_res.status_code == 200:
                    props = db_res.json().get("properties", {})
                    cols = list(props.keys())
                    print(f"       Columns: {cols}")
                    
                    # 嘗試讀取該資料庫的前幾筆資料
                    query_res = http_client.post(f"{base_url}/databases/{db_id}/query")
                    query_res.raise_for_status()
                    rows = query_res.json().get("results", [])
                    if rows:
                        print(f"       First row preview:")
                        row_data = {}
                        for col in cols:
                            p = rows[0].get("properties", {}).get(col, {})
                            ptype = p.get("type")
                            if ptype == "title" and p["title"]: row_data[col] = p["title"][0]["plain_text"]
                            elif ptype == "rich_text" and p["rich_text"]: row_data[col] = p["rich_text"][0]["plain_text"]
                            elif ptype == "select" and p["select"]: row_data[col] = p["select"]["name"]
                            elif ptype == "people" and p["people"]: row_data[col] = p["people"][0]["name"]
                            else: row_data[col] = ""
                        print(f"       {row_data}")
                    else:
                        print("       (Database is empty)")
                else:
                    print(f"       Could not fetch database details (Status: {db_res.status_code})")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        http_client.close()

if __name__ == "__main__":
    analyze_section("34caad32-6752-80f5-af7a-d9bf558374dc", "上期未完成及本期討論項目")
