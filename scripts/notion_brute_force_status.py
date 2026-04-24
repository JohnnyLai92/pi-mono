import os
from dotenv import load_dotenv
import httpx

load_dotenv()

def brute_force_status(page_id, target_status="Todo"):
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
        print(f"Attempting to find any 'select' property to set as status for {page_id}...")
        page_res = http_client.get(f"{base_url}/pages/{page_id}")
        page_res.raise_for_status()
        properties = page_res.json().get("properties", {})
        
        status_col = None
        for p_name, p_info in properties.items():
            if p_info.get("type") == "select":
                print(f"Found potential status column: '{p_name}' (type: select)")
                status_col = p_name
                break
        
        if not status_col:
            print("No 'select' type property found. Cannot set status.")
            return

        print(f"Updating '{status_col}' to '{target_status}'...")
        payload = {
            "properties": {
                status_col: {
                    "select": {"name": target_status}
                }
            }
        }
        
        update_res = http_client.patch(f"{base_url}/pages/{page_id}", json=payload)
        if update_res.status_code == 200:
            print("✅ SUCCESS: Status updated!")
        else:
            print(f"❌ FAILED: {update_res.status_code} - {update_res.text}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        http_client.close()

if __name__ == "__main__":
    TARGET_PAGE_ID = "34caad32-6752-80f5-af7a-d9bf558374dc"
    brute_force_status(TARGET_PAGE_ID, "Todo")
