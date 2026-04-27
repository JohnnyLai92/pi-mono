import os
import requests
from typing import List, Dict, Any

def clear_notion_page_content(token, page_id):
    # In Notion API, clearing a page typically means archiving its children blocks
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    # Get all blocks first
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code != 200:
        return f"Error fetching blocks: {response.text}"
    
    blocks = response.json().get("results", [])
    
    # Archive each block
    results = []
    for block in blocks:
        block_id = block["id"]
        archive_url = f"https://api.notion.com/v1/blocks/{block_id}"
        archive_payload = {"archived": True}
        archive_res = requests.patch(archive_url, json=archive_payload, headers=headers, verify=False)
        results.append(archive_res.status_code)
    
    return f"Archived {len(blocks)} blocks. Results: {results}"

if __name__ == "__main__":
    token = os.getenv("NOTION_TOKEN")
    page_id = "34caad32-6752-8127-a846-eed9a69e0de5"
    print(clear_notion_page_content(token, page_id))
