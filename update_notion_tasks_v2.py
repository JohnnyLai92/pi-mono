import os
import requests
from dotenv import load_dotenv

load_dotenv()

def archive_pages(page_ids):
    token = os.getenv("NOTION_TOKEN")
    base_url = "https://api.notion.com/v1"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    results = []
    for pid in page_ids:
        try:
            res = requests.patch(f"{base_url}/pages/{pid}", headers=headers, json={"archived": True})
            results.append(f"Page {pid}: {res.status_code}")
        except Exception as e:
            results.append(f"Page {pid} Error: {str(e)}")
    return results

def create_page(title, status):
    token = os.getenv("NOTION_TOKEN")
    db_id = os.getenv("NOTION_DATABASE_ID")
    base_url = "https://api.notion.com/v1"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    # Based on DB schema: Title property is '名稱', Status property is '狀態'
    # Valid Status options: '未開始', '進行中', '完成'
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
    # 1. Remove existing tasks
    to_remove = ["34caad32675280f5af7ad9bf558374dc", "34caad32675281488923df660f933269"]
    print("Archiving old tasks...")
    print(archive_pages(to_remove))
    
    # 2. Add new tasks with correct property names and status values
    new_tasks = [
        ("pi agent與NOTION串接整合", "進行中"),
        ("操作pi agent CURD Notion工作清單", "進行中")
    ]
    print("\nCreating new tasks...")
    for title, status in new_tasks:
        print(create_page(title, status))
