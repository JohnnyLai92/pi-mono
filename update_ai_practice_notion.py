import os
import requests
from dotenv import load_dotenv

load_dotenv()

def append_ai_practice(title, content):
    token = os.getenv("NOTION_TOKEN")
    base_url = "https://api.notion.com/v1"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    # 1. Find the page ID for "AI 中級應用規劃師題型練習"
    # We'll search for the page first
    search_res = requests.post(f"{base_url}/search", headers=headers, json={"query": "AI 中級應用規劃師題型練習"})
    pages = search_res.json().get("results", [])
    page_id = None
    for p in pages:
        if p["object"] == "page":
            page_id = p["id"]
            break
    
    if not page_id:
        return "Could not find the practice page."

    # 2. Build the content blocks for today's practice (Sample content since we haven't run today's test yet)
    # In real execution, this will be passed as an argument.
    blocks = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": title}}] }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}] }
        }
    ]
    
    url = f"{base_url}/blocks/{page_id}/children"
    res = requests.patch(url, headers=headers, json={"children": blocks})
    return f"Updated: {res.status_code}"

if __name__ == "__main__":
    # Today's summary (as a placeholder since actual test hasn't run in this session)
    print(append_ai_practice("2026-04-24 初始同步", "已啟動 AI 中級應用規劃師自動同步機制。後續的每日練習題及其解析將自動同步至此頁面。"))
