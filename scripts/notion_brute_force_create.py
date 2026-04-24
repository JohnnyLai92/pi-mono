import os
from dotenv import load_dotenv
import httpx

load_dotenv()

def create_with_existing_option(page_id, db_id):
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
        print("1. Fetching database schema to find valid options...")
        db_res = http_client.get(f"{base_url}/databases/{db_id}")
        db_res.raise_for_status()
        props = db_res.json().get("properties", {})
        
        status_col = None
        valid_options = []

        for p_name, p_info in props.items():
            if p_info.get("type") == "status":
                status_col = p_name
                # 抓取 status 欄位中所有的 options
                # 注意：status 類型的選項在 schema 中是 status 屬性
                valid_options = [opt["name"] for opt in p_info.get("status", {}).get("options", [])]
                break
        
        if not status_col:
            print("Could not find a status column.")
            return

        print(f"Found status column: '{status_col}'")
        print(f"Available options in Notion: {valid_options}")

        if not valid_options:
            print("No options found in status column. Using a default one...")
            # 如果真的沒選項，嘗試建立一個 (這可能會失敗，因為 status 類型通常預設有選項)
            valid_options = ["未開始"] 

        target_option = valid_options[0]
        print(f"Using first available option: '{target_option}'")

        print(f"2. Creating page with '{target_option}'...")
        payload = {
            "parent": {"database_id": db_id},
            "properties": {
                "名稱": {
                    "title": [{"text": {"content": "m20260424"}}]
                },
                status_col: {
                    "status": {"name": target_option}
                }
            }
        }
        
        res = http_client.post(f"{base_url}/pages", json=payload)
        if res.status_code == 200:
            print("✅ SUCCESS: Meeting page created successfully!")
        else:
            print(f"❌ FAILED: {res.status_code} - {res.text}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        http_client.close()

if __name__ == "__main__":
    TARGET_PAGE_ID = "34caad32-6752-80f5-af7a-d9bf558374dc"
    TARGET_DB_ID = "34caad32-6752-8041-9295-fac5ed2ffdee"
    create_with_existing_option(TARGET_PAGE_ID, TARGET_DB_ID)
