import os
import requests
import json

token = os.getenv("NOTION_TOKEN")
# 根據剛才 curl 的結果，我手動抓取 "20250422會議紀錄" 的 ID (這是在回應的第一個物件)
# 根據剛才的 output，第一個 page 的 id 是從 id 欄位抓取的，但剛才的 output 被截斷了。
# 我改用 Search API 加上 filter 來精確定位該頁面。

def get_page_by_title(title_text):
    url = "https://api.notion.com/v1/search"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    # 這裡無法直接用 search API 根據 title filter，所以我們還是先 search 拿全部，再從裡面找
    payload = {"query": title_text, "filter": {"value": "page", "property": "object"}}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        results = response.json().get("results", [])
        for obj in results:
            if obj["object"] == "page":
                # 檢查 title (這部分邏輯較複雜，因為不同 page 結構不同)
                # 我們嘗試抓取 properties 裡的 title
                props = obj.get("properties", {})
                for p in props.values():
                    if p.get("type") == "title":
                        title_list = p.get("title", [])
                        if title_list and title_list[0].get("plain_text") == title_text:
                            return obj["id"]
    return None

def read_page_content(page_id):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Failed to fetch page: {response.status_code}, {response.text}"}

# 使用者輸入 20260422，我假設他是要 20250422
target_title = "20250422會議紀錄" 
print(f"Searching for page: {target_title}...")
page_id = get_page_by_title(target_title)

if page_id:
    print(f"Found Page ID: {page_id}")
    content = read_page_content(page_id)
    print("--- PAGE CONTENT (STRUCTURE) ---")
    print(json.dumps(content, indent=2, ensure_ascii=False))
else:
    print(f"Could not find page with title: {target_title}")

