import os
import requests
from dotenv import load_dotenv

load_dotenv()

def create_page(title, status):
    token = os.getenv("NOTION_TOKEN")
    db_id = os.getenv("NOTION_DATABASE_ID")
    base_url = "https://api.notion.com/v1"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    payload = {
        "parent": {"database_id": db_id},
        "properties": {
            "名稱": {
                "title": [{"text": {"content": title}}]
            },
            "狀態": {
                "status": {"name": status}
            }
        }
    }
    
    try:
        res = requests.post(f"{base_url}/pages", headers=headers, json=payload)
        res.raise_for_status()
        return f"Created: {title} ({res.status_code})"
    except Exception as e:
        return f"Failed to create {title}: {str(e)}"

if __name__ == "__main__":
    print(create_page("AI 中級應用規劃師題型練習", "進行中"))
