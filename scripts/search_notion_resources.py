import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")

def search_notion_resources():
    url = "https://api.notion.com/v1/search"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    # 搜尋所有內容 (pages, databases, etc.)
    params = {}
    
    try:
        print("Searching for accessible Notion resources...")
        response = requests.post(url, headers=headers, json=params, verify=False)
        response.raise_for_status()
        data = response.json()
        
        results = data.get('results', [])
        if not results:
            print("No resources found.")
            return

        print(f"\nFound {len(results)} accessible resources:\n")
        print(f"{'Type':<15} | {'Name':<30} | {'ID'}")
        print("-" * 70)
        
        for item in results:
            obj_type = item.get('object')
            # 處理名稱 (Notion 的名稱結構因類型而異)
            name = "Unknown"
            if obj_type == 'database':
                # Database 的名稱在 title 屬性中
                title_prop = item.get('title', [])
                if title_prop:
                    name = title_prop[0].get('plain_text', 'No Title')
            elif obj_type == 'page':
                # Page 的名稱在 properties 的 title 欄位中
                props = item.get('properties', {})
                for p in props.values():
                    if p.get('type') == 'title':
                        title_list = p.get('title', [])
                        if title_list:
                            name = title_list[0].get('plain_text', 'No Title')
                        break
            
            print(f"{obj_type:<15} | {name[:30]:<30} | {item['id']}")

    except Exception as e:
        print(f"Search failed: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    search_notion_resources()
