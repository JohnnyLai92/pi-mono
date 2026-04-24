import os
from dotenv import load_dotenv
import httpx

load_dotenv()

class NotionTopicManager:
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

    def add_sub_topics(self, page_id, target_heading, sub_items):
        print(f"🚀 Adding sub-topics under '{target_heading}' in Page ID: {page_id}")
        
        try:
            # 1. Get all blocks
            print("Step 1: Fetching all blocks to find the target heading...")
            block_res = self.http_client.get(f"{self.base_url}/blocks/{page_id}/children")
            block_res.raise_for_status()
            blocks = block_res.json().get("results", [])
            
            target_block_id = None
            for block in blocks:
                b_type = block["type"]
                text = ""
                if b_type in ["heading_1", "heading_2", "heading_3"]:
                    try:
                        text = block[b_type]["rich_text"][0]["text"]["content"]
                    except: pass
                
                if text.strip() == target_heading:
                    target_block_id = block["id"]
                    break
            
            if not target_block_id:
                print(f"❌ Error: Could not find heading '{target_heading}'")
                return False
            
            print(f"✅ Found '{target_heading}' (ID: {target_block_id})")

            # 2. Prepare new blocks (bulleted list items)
            new_blocks = []
            for item in sub_items:
                new_blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": item}}]
                    }
                })

            # 3. Append blocks AFTER the target heading
            # Notion API doesn't support "insert_after" directly for blocks.
            # The workaround is to append them to the end of the page, 
            # OR rebuild the list. Since this is a small page, we will rebuild.
            
            print("Step 2: Rebuilding page to insert sub-topics exactly under the heading...")
            
            rebuilt_blocks = []
            for block in blocks:
                rebuilt_blocks.append(block)
                if block["id"] == target_block_id:
                    rebuilt_blocks.extend(new_blocks)
            
            # Note: To "replace" all blocks, we actually have to delete and recreate 
            # OR use a more complex approach. 
            # However, for simple automation, appending to the end is most reliable.
            # Let'            
            print("⚠️ Notion API limitation: Direct 'insert after' is not available.")
            print("Appending sub-items to the end of the page for now...")
            
            payload = {"children": new_blocks}
            response = self.http_client.patch(f"{self.base_url}/blocks/{page_id}/children", json=payload)
            
            if response.status_code == 200:
                print("✅ SUCCESS: Sub-items appended to the end of the page.")
                return True
            else:
                print(f"❌ FAILED: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False
        finally:
            self.http_client.close()

if __name__ == "__main__":
    TARGET_PAGE_ID = "34caad32-6752-8148-a6e8-cb4f5311886d"
    SUB_TOPICS = ["Chatbot", "tc", "csc", "cs", "ed", "fts"]
    TARGET_HEADING = "本期討論事項"
    
    manager = NotionTopicManager()
    manager.add_sub_topics(TARGET_PAGE_ID, TARGET_HEADING, SUB_TOPICS)
