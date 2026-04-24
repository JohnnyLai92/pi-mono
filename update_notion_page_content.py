import os
import requests
from dotenv import load_dotenv

load_dotenv()

def append_content(page_id, content_blocks):
    token = os.getenv("NOTION_TOKEN")
    base_url = "https://api.notion.com/v1"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    # We use the blocks API to append children to the page
    url = f"{base_url}/blocks/{page_id}/children"
    
    # Notion API only allows adding a few blocks per request, but we can batch them.
    # We will send the content as a list of block objects.
    payload = {
        "children": content_blocks
    }
    
    try:
        res = requests.patch(url, headers=headers, json=payload)
        res.raise_for_status()
        return f"Successfully updated page {page_id}"
    except Exception as e:
        return f"Error updating page: {str(e)}"

if __name__ == "__main__":
    page_id = "34caad3267528151b6c5fbec3fd53cad"
    
    # Constructing the content to represent our journey
    blocks = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🛠️ 串接整合紀錄"}}] }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": "記錄 pi agent 整合 Notion API 過程中遇到的問題與解決方案。"}}] }
        },
        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [{"type": "text", "text": {"content": "1. 讀取範圍與效能問題"}}] }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "問題：使用 /search 全域搜尋導致抓取大量無關頁面，且效能低且不準確。"}}] }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "解決方案：將 API 改用 /databases/{id}/query，精確鎖定特定工作資料庫。"}}] }
        },
        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [{"type": "text", "text": {"content": "2. 分頁數據遺漏"}}] }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "問題：Notion API 單次僅回傳 100 筆，導致大量工作項遺漏。"}}] }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "解決方案：實作 _paginate 通用方法，透過 next_cursor 遞迴抓取所有數據。"}}] }
        },
        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [{"type": "text", "text": {"content": "3. 400 Bad Request 錯誤"}}] }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "問題：使用不正確的 filter 運算子 (is_not) 導致伺服器錯誤。"}}] }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "解決方案：諮詢 Claude 後決定移除複雜的服務端過濾，改用高效的客戶端過濾邏輯。"}}] }
        },
        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [{"type": "text", "text": {"content": "4. 屬性名稱不匹配"}}] }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "問題：預設使用 English (Name/Status) 導致無法創建頁面。"}}] }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "解決方案：透過分析 DB Schema 將屬性修正為中文化名稱 ('名稱', '狀態')。"}}] }
        }
    ]
    
    print(append_content(page_id, blocks))
