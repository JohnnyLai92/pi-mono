import os
import logging
from dotenv import load_dotenv
import httpx

load_dotenv()

def extract_todos(title_query):
    token = os.getenv("NOTION_TOKEN")
    base_url = "https://api.notion.com/v1"
    
    http_client = httpx.Client(
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        },
        verify=False
    )

    try:
        # 1. 搜尋頁面
        search_res = http_client.post(f"{base_url}/search", json={"query": title_query})
        search_res.raise_for_status()
        results = search_res.json().get("results", [])
        if not results:
            print("找不到頁面")
            return
        
        page_id = results[0]["id"]
        
        # 2. 取得 Blocks
        block_res = http_client.get(f"{base_url}/blocks/{page_id}/children")
        block_res.raise_for_status()
        blocks = block_res.json().get("results", [])
        
        print(f"正在從頁面 '{title_query}' 提取待辦事項...\n")
        
        found_any = False
        for block in blocks:
            b_type = block["type"]
            # Notion 的待辦事項通常是 checked: false 的 to_do block
            if b_type == "to_do":
                todo_data = block["to_do"]
                text = ""
                if todo_data.get("rich_text"):
                    text = todo_data["rich_text"][0]["text"]["content"]
                
                status = "[ ]" if not todo_data.get("checked") else "[x]"
                if text:
                    print(f"{status} {text}")
                    found_any = True
            
            # 有時候待辦事項會寫在 bulleted_list_item 裡，但沒有勾選框
            elif b_type == "bulleted_list_item":
                text = ""
                if block["bulleted_list_item"].get("rich_text"):
                    text = block["bulleted_list_item"]["rich_text"][0]["text"]["content"]
                if text:
                    # 這裡我們假設 bulleted list 裡的內容可能包含待辦暗示，先列出來
                    # 但為了精準，我們主要找 to_do 類型
                    pass

        if not found_any:
            print("未在頁面中發現明確的 'To-do list' 區塊。")
            print("正在嘗試掃描所有文字內容中的關鍵字 (如 '待辦', 'TODO', 'Action Items')...")
            # 備案：掃描所有文字內容
            for block in blocks:
                b_type = block["type"]
                text = ""
                if b_type in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item"]:
                    try:
                        text = block[b_type]["rich_text"][0]["text"]["content"]
                    except: pass
                
                if any(kw in text for kw in ["待辦", "TODO", "Action", "事項", "未完成"]):
                    print(f"發現相關內容: {text}")
                    found_any = True

    except Exception as e:
        print(f"錯誤: {e}")
    finally:
        http_client.close()

if __name__ == "__main__":
    extract_todos("m20260422")
