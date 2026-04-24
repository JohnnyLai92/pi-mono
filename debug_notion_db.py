import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_db_schema():
    token = os.getenv("NOTION_TOKEN")
    db_id = os.getenv("NOTION_DATABASE_ID")
    url = f"https://api.notion.com/v1/databases/{db_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28"
    }
    res = requests.get(url, headers=headers)
    return res.json()

if __name__ == "__main__":
    print(get_db_schema())
