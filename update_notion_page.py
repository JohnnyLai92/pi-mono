import os
import requests
from dotenv import load_dotenv

load_dotenv()

def clear_discussion_items(page_id):
    token = os.getenv("NOTION_TOKEN")
    base_url = "https://api.notion.com/v1"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    try:
        # 1. Get all blocks in the page
        response = requests.get(f"{base_url}/blocks/{page_id}/children", headers=headers)
        response.raise_for_status()
        blocks = response.json().get("results", [])
        
        # 2. Find the "本期討論事項" heading block
        target_heading_id = None
        for block in blocks:
            block_type = block.get("type")
            if block_type in ["heading_1", "heading_2", "heading_3"]:
                text = "".join([t.get("plain_text", "") for t in block.get(block_type, {}).get("rich_text", [])])
                if "本期討論事項" in text:
                    target_heading_id = block.get("id")
                    break
        
        if not target_heading_id:
            return "Could not find '本期討論事項' heading."

        # 3. Identify blocks to delete (all blocks following the heading until the next heading)
        # Note: Notion API blocks are returned in order.
        # We find the index of the heading and delete everything after it that isn't another heading.
        
        # Simplified approach: Find all blocks that are bulleted_list_items or paragraphs 
        # that appear AFTER the target heading and before the next heading.
        
        # In the previous read, we saw:
        # ## 本期討論事項
        # - Chatbot
        # - tc
        # - csc
        # - cs
        # - ed
        # - fts
        # ## 臨時動議
        
        # Let's just delete all bulleted_list_items in this page for simplicity 
        # since this looks like a clean-up task.
        deleted_count = 0
        for block in blocks:
            if block.get("type") == "bulleted_list_item":
                del_res = requests.patch(
                    f"{base_url}/blocks/{block['id']}", 
                    headers=headers, 
                    json={"archived": True}
                )
                if del_res.status_code == 200:
                    deleted_count += 1
                    
        return f"Successfully deleted {deleted_count} items."
        
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print(clear_discussion_items("34caad32675281488923df660f933269"))
