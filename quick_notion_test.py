import os
import requests
import sys

# 模擬載入 .env 的邏輯
env_path = '.env'
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

class NotionQuickTest:
    def __init__(self):
        self.token = os.getenv("NOTION_TOKEN")
        self.base_url = "https://api.notion.com/v1"

    def test(self):
        if not self.token:
            print("ERROR: NOTION_TOKEN not found in environment.")
            return

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

        print(f"Attempting to connect to Notion with token: {self.token[:8]}***")
        
        try:
            # 使用 Search API
            response = requests.post(f"{self.base_url}/search", headers=headers, json={})
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                print(f"SUCCESS! Found {len(results)} items.")
                
                if not results:
                    print("No pages or databases found in your Notion workspace.")
                    print("Tip: Ensure your Notion Integration has access to the pages/databases.")
                else:
                    print("\n--- List of Pages/Databases ---")
                    for obj in results:
                        if obj["object"] == "page":
                            # 嘗試抓取標題 (簡化版)
                            title = "Untitled"
                            props = obj.get("properties", {})
                            for p in props.values():
                                if p.get("type") == "title":
                                    title_list = p.get("title", [])
                                    if title_list:
                                        title = title_list[0].get("plain_text", "Untitled")
                                    break
                            print(f"- [Page] {title} (ID: {obj['id']})")
                        elif obj["object"] == "database":
                            print(f"- [Database] ID: {obj['id']}")
            else:
                print(f"FAILED! Status Code: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    tester = NotionQuickTest()
    tester.test()
