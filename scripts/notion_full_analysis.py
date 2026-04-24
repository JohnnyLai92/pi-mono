import os
from dotenv import load_dotenv
import httpx

load_dotenv()

class NotionAnalyzer:
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

    def analyze_page(self, page_id):
        print(f"--- START ANALYSIS: {page_id} ---\n")
        
        try:
            # 1. 取得頁面屬性 (Properties)
            print("[STEP 1] Fetching properties...")
            page_res = self.http_client.get(f"{self.base_url}/pages/{page_id}")
            page_res.raise_for_status()
            page_data = page_res.json()
            
            print("\n[SECTION: PROPERTIES]")
            properties = page_data.get("properties", {})
            if not properties:
                print("  (No properties found)")
            else:
                for prop_name, prop_info in properties.items():
                    p_type = prop_info.get("type")
                    val = "N/A"
                    
                    if p_type == "title" and prop_info["title"]:
                        val = prop_info["title"][0]["plain_text"]
                    elif p_type == "select" and prop_info["select"]:
                        val = prop_info["select"]["name"]
                    elif p_type == "people" and prop_info["people"]:
                        val = ", ".join([p["name"] for p in prop_info["people"]])
                    elif p_type == "checkbox":
                        val = str(prop_info["checkbox"])
                    elif p_type == "multi_select":
                        val = ", ".join([s["name"] for s in prop_info["multi_select"]])
                    elif p_type == "date" and prop_info["date"]:
                        val = prop_info["date"]["start"]
                    elif p_type == "rich_text" and prop_info["rich_text"]:
                        val = prop_info["rich_text"][0]["plain_text"]
                    
                    print(f"  - {prop_name} ({p_type}): {val}")
            print()

            # 2. 取得頁面內容 (Blocks)
            print("[STEP 2] Fetching block content...")
            block_res = self.http_client.get(f"{self.base_url}/blocks/{page_id}/children")
            block_res.raise_for_status()
            blocks = block_res.json().get("results", [])
            
            print("\n[SECTION: BODY CONTENT]")
            if not blocks:
                print("  (No content blocks found)")
            else:
                for block in blocks:
                    b_type = block["type"]
                    text = ""
                    if b_type in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "to_do"]:
                        try:
                            text = block[b_type]["rich_text"][0]["text"]["content"]
                        except:
                            text = ""
                    
                    if text.strip():
                        print(f"  * [{b_type}] {text}")
            
            print("\n--- ANALYSIS COMPLETE ---")

        except Exception as e:
            print(f"ERROR: {e}")
        finally:
            self.http_client.close()

if __name__ == "__main__":
    TARGET_PAGE_ID = "34caad32-6752-80f5-af7a-d9bf558374dc"
    analyzer = NotionAnalyzer()
    analyzer.analyze_page(TARGET_PAGE_ID)
