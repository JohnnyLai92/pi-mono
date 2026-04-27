import os
import requests
import json

def check_notion_structure(token, page_id):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    res = requests.get(url, headers=headers, verify=False)
    if res.status_code != 200:
        return f"Error: {res.status_code}"
    
    blocks = res.json().get("results", [])
    print(f"Total top-level blocks: {len(blocks)}")
    
    for b in blocks:
        if b.get("type") == "heading_4":
            q_id = b["id"]
            q_text = "".join([t.get("plain_text", "") for t in b["heading_4"]["rich_text"]])
            print(f"Checking Toggle: {q_text[:20]}...")
            
            child_url = f"https://api.notion.com/v1/blocks/{q_id}/children"
            child_res = requests.get(child_url, headers=headers, verify=False)
            children = child_res.json().get("results", [])
            
            has_answer = any(c.get("type") == "callout" and c["callout"].get("icon", {}).get("emoji") == "✏️" for c in children)
            has_feedback = any(c.get("type") == "callout" and c["callout"].get("icon", {}).get("emoji") == "🤖" for c in children)
            
            print(f"  - Answer Block: {'YES' if has_answer else 'NO'}")
            print(f"  - Feedback Block: {'YES' if has_feedback else 'NO'}")

if __name__ == "__main__":
    import sys
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass
    token = os.getenv("NOTION_TOKEN")
    page_id = "34caad32-6752-8127-a846-eed9a69e0de5"
    check_notion_structure(token, page_id)
