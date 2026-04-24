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
    url = f"{base_url}/blocks/{page_id}/children"
    payload = {"children": content_blocks}
    try:
        res = requests.patch(url, headers=headers, json=payload)
        res.raise_for_status()
        return f"Successfully updated page {page_id}"
    except Exception as e:
        return f"Error updating page: {str(e)}"

if __name__ == "__main__":
    page_id = "34caad32675281339419da3c9311262b"
    
    blocks = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🛠️ CURD 操作實現紀錄"}}] }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": "記錄 pi agent 如何實現對 Notion 資料庫的 Create, Read, Update, Delete 操作。"}}] }
        },
        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [{"type": "text", "text": {"content": "1. Create (新增工作)"}}] }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "方法：使用 POST /pages API。"}}] }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "關鍵解決方案：必須精確匹配資料庫屬性名稱（如 '名稱'、'狀態'）及預定義的 Option 值（如 '進行中'），否則會觸發 400 錯誤。"}}] }
        },
        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [{"type": "text", "text": {"content": "2. Read (讀取工作)"}}] }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "方法：使用 /databases/{id}/query a la 與分頁遞迴抓取。"}}] }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "優化：實作客戶端過濾 logic，確保過濾結果的靈活性與兼容性。"}}] }
        },
        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [{"type": "text", "text": {"content": "3. Update (更新屬性)"}}] }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "方法：使用 PATCH /pages/{page_id} API。"}}] }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "應用場景：修改工作狀態、更新標題或更新頁面內容。"}}] }
        },
        {
            "object": "block",
            "type": "heading_3",
            "heading_3": {"rich_text": [{"type": "text", "text": {"content": "4. Delete (刪除/封存工作)"}}] }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "方法：使用 PATCH /pages/{page_id} 並將 'archived' 設為 True。"}}] }
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "經驗教訓：在刪除特定標題下的區塊時，必須精確控制刪除範圍（不能全頁刪除），否則會導致非目標數據被誤刪。"}}] }
        }
    ]
    
    print(append_content(page_id, blocks))
