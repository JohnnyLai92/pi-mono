import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
# 我們需要找到包含 "DGT1 定期會議20260422" 的頁面 ID
# 由於我目前只有 Database ID，我會先列出該資料庫下的所有頁面來搜尋

def test_read_notion_database(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        response = requests.post(url, headers=headers, verify=False)
        response.raise_for_status()
        data = response.json()
        
        print(f"Successfully queried database. Found {len(data['results'])} pages.\n")
        
        target_title = "DGTK 定期會議20260422"
        found_page_id = None
        
        for page in data['results']:
            # 嘗試從 properties 中找到標題 (通常是 'Name' 或 'title')
            # Notion 的標題欄位名稱可能因資料庫設定而異，這裡做通用處理
            properties = page.get('properties', {})
            for prop_name, prop_val in properties.items():
                if prop_val.get('type') == 'title':
                    titles = prop_val.get('title', [])
                    if titles and titles[0].get('plain_text') == target_title:
                        found_page_id = page['id']
                        print(f"🎯 Found target page: {target_title} (ID: {found_page_id})")
                        break
            if found_page_id:
                break
        
        if not found_page_id:
            print(f"❌ Could not find page with title: {target_title}")
            print("Available page titles in this database:")
            for page in data['results']:
                for prop_name, prop_val in page.get('properties', {}).items():
                    if prop_val.get('type') == 'title':
                        t = prop_val.get('title', [])
                        if t: print(f" - {t[0].get('plain_text')}")
        else:
            # 如果找到了，接著讀取該頁面的內容 (Blocks)
            print(f"\nFetching content for page {found_page_id}...")
            block_url = f"https://api.notion.com/v1/blocks/{found_page_id}/children"
            block_res = requests.get(block_url, headers=headers, verify=False)
            block_res.raise_for_status()
            blocks = block_res.json().get('results', [])
            
            print("\n--- Page Content Preview ---")
            for block in blocks:
                block_type = block.get('type')
                if block_type in ['paragraph', 'heading_1', 'heading_2', 'heading_3', 'to_do']:
                    content = block[block_type].get('rich_text', [])
                    text = "".join([t.get('plain_text', '') for t in content])
                    if text:
                        print(f"[{block_type}] {text}")
            print("--- End of Preview ---\n")
            print("✅ Read successful! Now I can proceed to extract To-do items.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    DATABASE_ID = "34caad32675280419295fac5ed2ffdee"
    test_read_notion_database(DATABASE_ID)
