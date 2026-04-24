import os
from dotenv import load_dotenv
import httpx
import json

load_dotenv()

def dump_raw_properties(page_id):
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
        print(f"Fetching RAW properties for Page ID: {page_id}...")
        response = http_client.get(f"{base_url}/pages/{page_id}")
        response.raise_for_status()
        
        data = response.json()
        properties = data.get("properties", {})
        
        print("\n--- RAW PROPERTY DATA START ---")
        # 將整個 properties 字典轉成 JSON 並寫入檔案，避免 Terminal 亂碼問題
        with open("raw_properties_dump.json", "w", encoding="utf-8") as f:
            json.dump(properties, f, ensure_ascii=False, indent=4)
        
        print("✅ Dumped to 'raw_properties_dump.json'")
        print(f"Total properties found: {len(properties)}")
        print("--- RAW PROPERTY DATA END ---\n")

        # 同時在螢幕上印出簡易列表，幫助判斷
        for name in properties.keys():
            # 這裡不直接印出內容，只印出 Key，避免編碼噴錯
            print(f"Key detected: {name}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        http_client.close()

if __name__ == "__main__":
    TARGET_PAGE_ID = "34caad32-6752-80f5-af7a-d9bf558374dc"
    dump_raw_properties(TARGET_PAGE_ID)
