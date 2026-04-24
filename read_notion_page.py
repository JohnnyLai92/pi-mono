import os
import requests
from dotenv import load_dotenv

load_dotenv()

def read_page(page_id):
    token = os.getenv("NOTION_TOKEN")
    base_url = "https://api.notion.com/v1"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    try:
        # Retrieve page properties and content
        response = requests.get(f"{base_url}/blocks/{page_id}/children", headers=headers)
        response.raise_for_status()
        data = response.json()
        
        blocks = data.get("results", [])
        content = []
        for block in blocks:
            block_type = block.get("type")
            if block_type == "paragraph":
                rich_text = block.get("paragraph", {}).get("rich_text", [])
                text = "".join([t.get("plain_text", "") for t in rich_text])
                content.append(text)
            elif block_type == "heading_1":
                text = "".join([t.get("plain_text", "") for t in block.get("heading_1", {}).get("rich_text", [])])
                content.append(f"# {text}")
            elif block_type == "heading_2":
                text = "".join([t.get("plain_text", "") for t in block.get("heading_2", {}).get("rich_text", [])])
                content.append(f"## {text}")
            elif block_type == "heading_3":
                text = "".join([t.get("plain_text", "") for t in block.get("heading_3", {}).get("rich_text", [])])
                content.append(f"### {text}")
            elif block_type == "bulleted_list_item":
                text = "".join([t.get("plain_text", "") for t in block.get("bulleted_list_item", {}).get("rich_text", [])])
                content.append(f"- {text}")
            elif block_type == "numbered_list_item":
                text = "".join([t.get("plain_text", "") for t in block.get("numbered_list_item", {}).get("rich_text", [])])
                content.append(f"1. {text}")
        
        return "\n".join(content)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # page_id from previous list: 34caad32675281488923df660f933269
    print(read_page("34caad32675281488923df660f933269"))
