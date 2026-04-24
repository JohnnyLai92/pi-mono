import os
from dotenv import load_dotenv
import httpx

load_dotenv()

def check_page_properties(page_id):
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
        print(f"Fetching properties for Page ID: {page_id}...\n")
        response = http_client.get(f"{base_url}/pages/{page_id}")
        response.raise_for_status()
        page_data = response.json()
        
        properties = page_data.get("properties", {})
        
        if not properties:
            print("This page has no properties.")
            return

        print(f"--- Page Properties List ---")
        for prop_name, prop_info in properties.items():
            p_type = prop_info.get("type")
            val_str = ""
            
            if p_type == "title":
                if prop_info["title"]:
                    val_str = prop_info["title"][0]["plain_text"]
            elif p_type == "rich_text":
                if prop_info["rich_text"]:
                    val_str = prop_info["rich_text"][0]["plain_text"]
            elif p_type == "select":
                if prop_info["select"]:
                    val_str = prop_info["select"]["name"]
            elif p_type == "multi_select":
                val_str = ", ".join([s["name"] for s in prop_info["multi_select"]])
            elif p_type == "date":
                if prop_info["date"]:
                    val_str = prop_info["date"]["start"]
            elif p_type == "checkbox":
                val_str = str(prop_info["checkbox"])
            elif p_type == "people":
                if prop_info["people"]:
                    val_str = ", ".join([p["name"] for p in prop_info["people"]])
            elif p_type == "relation":
                val_str = f"{len(prop_info['relation'])} items linked"
            
            print(f"[{p_type.upper()}] {prop_name}: {val_str}")
        print("-" * 35)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        http_client.close()

if __name__ == "__main__":
    TARGET_PAGE_ID = "34caad32-6752-80f5-af7a-d9bf558374dc"
    check_page_properties(TARGET_PAGE_ID)
