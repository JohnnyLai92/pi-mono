import os
from dotenv import load_dotenv
import httpx

load_dotenv()

class NotionRecursiveScanner:
    def __init__(self):
        self.token = os.getenv("NOTION_TOKEN")
        self.base_url = "https://api.notion.com/v1"
        self.http_client = httpx.Client(
            headers={
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            },
            verify=False
        )
        self.visited_ids = set()

    def scan(self, page_id, depth=0):
        if page_id in self.visited_ids or depth > 5:
            return
        self.visited_ids.add(page_id)
        
        indent = "  " * depth
        print(f"{indent}🔍 Scanning Page ID: {page_id}")

        try:
            # 1. 獲取頁面資訊 (取得標題)
            page_res = self.http_client.get(f"{self.base_url}/pages/{page_id}")
            if page_res.status_code == 200:
                page_data = page_res.json()
                title = "Untitled"
                props = page_data.get("properties", {})
                for p_name, p_val in props.items():
                    if p_val.get("type") == "title" and p_val["title"]:
                        title = p_val["title"][0]["plain_text"]
                        break
                print(f"{indent}📄 Page Title: {title}")
            else:
                print(f"{indent}⚠️ Could not fetch page title (Status: {page_res.status_code})")
            
            # 2. 獲取該頁面的 Blocks
            block_res = self.http_client.get(f"{self.base_url}/blocks/{page_id}/children")
            block_res.raise_for_status()
            blocks = block_res.json().get("results", [])

            for block in blocks:
                b_type = block["type"]
                
                # 處理文字內容
                if b_type in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "to_do"]:
                    try:
                        text = block[b_type]["rich_text"][0]["text"]["content"]
                        if text.strip():
                            print(f"{indent}  • [{b_type}] {text}")
                    except:
                        pass
                
                # 處理子頁面 (遞迴)
                elif b_type == "child_page":
                    child_id = block["id"]
                    self.scan(child_id, depth + 1)
                
                # 處理資料庫 (遞迴進入資料庫)
                elif b_type == "child_database":
                    print(f"{indent}  📊 Found Database! Scanning rows...")
                    self.scan_database(block["id"], depth + 1)

        except Exception as e:
            print(f"{indent}  ❌ Error: {e}")

    def scan_database(self, db_id, depth):
        indent = "  " * depth
        try:
            query_res = self.http_client.post(f"{self.base_url}/databases/{db_id}/query")
            query_res.raise_for_status()
            results = query_res.json().get("results", [])
            
            for page in results:
                props = page.get("properties", {})
                row_items = []
                for p_name, p_val in props.items():
                    p_type = p_val.get("type")
                    val = ""
                    if p_type == "title" and p_val["title"]:
                        val = p_val["title"][0]["plain_text"]
                    elif p_type == "rich_text" and p_val["rich_text"]:
                        val = p_val["rich_text"][0]["plain_text"]
                    elif p_type == "select" and p_val["select"]:
                        val = p_val["select"]["name"]
                    elif p_type == "people" and p_val["people"]:
                        val = p_val["people"][0]["name"]
                    
                    if val:
                        row_items.append(f"{p_name}: {val}")
                
                if row_items:
                    print(f"{indent}  Row: {' | '.join(row_items)}")
        except Exception as e:
            print(f"{indent}  ❌ DB Error: {e}")

if __name__ == "__main__":
    TARGET_PAGE_ID = "34caad32-6752-80f5-af7a-d9bf558374dc"
    scanner = NotionRecursiveScanner()
    scanner.scan(TARGET_PAGE_ID)
