import os
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import httpx

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

class NotionSyncManager:
    """
    使用 httpx 直接調用 Notion API 的管理員。
    具備自動偵測資料庫 Schema 與標題欄位名稱的功能。
    """
    def __init__(self):
        self.token = os.getenv("NOTION_TOKEN")
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        self.base_url = "https://api.notion.com/v1"
        
        if not self.token:
            logger.error("Missing NOTION_TOKEN in environment variables.")
        if not self.database_id:
            logger.error("Missing NOTION_DATABASE_ID in environment variables.")
            
        if self.token:
            self.http_client = httpx.Client(
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Notion-Version": "2022-06-28",
                    "Content-Type": "application/json"
                },
                verify=False
            )
        else:
            self.http_client = None

    def get_title_property_name(self, database_id: Optional[str] = None) -> Optional[str]:
        """
        自動偵測資料庫中哪一個欄位是 'title' 類型。
        """
        db_id = database_id or self.database_id
        if not self.http_client or not db_id:
            return None

        try:
            logger.info(f"Detecting title property for database: {db_id}")
            response = self.http_client.get(f"{self.base_url}/databases/{db_id}")
            response.raise_for_status()
            
            properties = response.json().get("properties", {})
            for prop_name, prop_info in properties.items():
                if prop_info.get("type") == "title":
                    logger.info(f"Detected title property name: '{prop_name}'")
                    return prop_name
            
            logger.warning("No property of type 'title' found in the database.")
            return None
        except Exception as e:
            logger.error(f"Failed to detect title property: {e}")
            return None

    def _md_to_notion_blocks(self, text: str) -> List[Dict[str, Any]]:
        """
        Markdown 轉 Notion Blocks 邏輯。
        """
        blocks = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('# '):
                blocks.append({
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]}
                })
            elif line.startswith('## '):
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {"rich_text": [{"type": "text", "text": {"content": line[3:]}}]}
                })
            elif line.startswith('### '):
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {"rich_text": [{"type": "text", "text": {"content": line[4:]}}]}
                })
            elif line.startswith('- ') or line.startswith('* '):
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]}
                })
            else:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": line}}]}
                })
        return blocks

    def sync_to_database(self, title: str, content: str, properties: Optional[Dict[str, Any]] = None):
        """
        將一條紀錄新增至指定的 Notion 資料庫。
        """
        if not self.http_client or not self.database_id:
            logger.error("Notion configuration is incomplete.")
            return False

        # 1. 自動找出標題欄位名稱
        title_col = self.get_title_property_name()
        if not title_col:
            logger.error("Could not determine the title property of the database. Sync aborted.")
            return False

        try:
            # 2. 建立新頁面 (Create Page)
            payload = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    title_col: {
                        "title": [{"text": {"content": title}}]
                    }
                }
            }
            
            if properties:
                payload["properties"].update(properties)

            response = self.http_client.post(f"{self.base_url}/pages", json=payload)
            response.raise_for_status()
            
            page_id = response.json()["id"]
            logger.info(f"Created new page: {title} (ID: {page_id}) using column '{title_col}'")

            # 3. 寫入內容 (Append Blocks)
            blocks = self._md_to_notion_blocks(content)
            if blocks:
                block_payload = {"children": blocks}
                block_response = self.http_client.patch(
                    f"{self.base_url}/blocks/{page_id}/children",
                    json=block_payload
                )
                block_response.raise_for_status()
                logger.info(f"Successfully synced content for: {title}")
            
            return True

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Failed to sync to Notion: {e}")
            return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Notion Sync Test Script")
    parser.add_argument("--title", type=str, help="Title of the page")
    parser.add_argument("--content", type=str, help="Content of the page (Markdown)")
    args = parser.parse_args()

    sync_manager = NotionSyncManager()
    
    if args.title and args.content:
        success = sync_manager.sync_to_database(args.title, args.content)
        if success:
            print("SUCCESS: Sync Successful!")
        else:
            print("FAILED: Sync Failed!")
    else:
        print("Usage: python scripts/notion_sync.py --title 'Test Title' --content '# Hello Notion\\nThis is a test.'")
