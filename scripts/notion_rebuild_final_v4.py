import os
from dotenv import load_dotenv
import httpx

load_dotenv()

class NotionPageRebuilder:
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

    def rebuild_with_subtopics(self, page_id, target_heading, sub_items):
        print(f"Starting HIGH-RISK Precision Rebuild for Page ID: {page_id}")
        print(f"Target Heading: {target_heading}")
        print(f"Sub-items: {sub_items}")

        try:
            # 1. Fetch all current blocks
            print("Step 1: Fetching current blocks...")
            block_res = self.http_client.get(f"{self.base_url}/blocks/{page_id}/children")
            block_res.raise_for_status()
            original_blocks = block_res.json().get("results", [])
            
            if not original_blocks:
                print("Error: Page is empty, nothing to rebuild.")
                return False

            # 2. Construct new sequence
            print("Step 2: Constructing new sequence...")
            new_sequence = []
            inserted = False
            
            for block in original_blocks:
                # Add the original block
                new_sequence.append(block)

                # Check if this is the target heading
                if not inserted and block["type"] in ["heading_1", "heading_2", "heading_3"]:
                    try:
                        text = block[block["type"]]["rich_text"][0]["text"]["content"]
                        if text.strip() == target_heading:
                            print(f"Found target heading: '{text}'")
                            for item in sub_items:
                                new_sequence.append({
                                    "object": "block",
                                    "type": "bulleted_list_item",
                                    "bulleted_list_item": {
                                        "rich_text": [{"type": "text", "text": {"content": item}}]
                                    }
                                })
                            inserted = True
                    except:
                        pass
            
            if not inserted:
                print("Warning: Target heading not found. Appending to end instead.")
                for item in sub_items:
                    new_sequence.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": item}}]
                        }
                    })

            # 3. Delete and Re-add
            print("Step 3: Clearing existing blocks (this may take a moment)...")
            for block in original_blocks:
                del_res = self.http_client.delete(f"{self.base_url}/blocks/{block['id']}")
                if del_res.status_code != 200:
                    # Some blocks might be protected or already gone
                    pass

            print("Step 4: Re-adding reconstructed sequence...")
            # Add in batches
            for i in range(0, len(new_sequence), 100):
                batch = new_sequence[i:i+100]
                payload = {"children": batch}
                res = self.http_client.patch(f"{self.base_url}/blocks/{page_id}/children", json=payload)
                if res.status_code != 200:
                    print(f"Batch error: {res.text}")
                    return False

            print("SUCCESS: Page rebuilt with precise ordering!")
            return True

        except Exception as e:
            print(f"ERROR: {e}")
            return False
        finally:
            self.http_client.close()

if __name__ == "__main__":
    TARGET_PAGE_ID = "34caad32-6752-8148-a6e8-cb4f5311886d"
    SUB_ITEMS = ["Chatbot", "tc", "csc", "cs", "ed", "fts"]
    TARGET_H = "本期討論事項"
    
    rebuilder = NotionPageRebuilder()
    rebuilder.rebuild_with_subtopics(TARGET_PAGE_ID, TARGET_H, SUB_ITEMS)
