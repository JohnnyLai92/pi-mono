import os
from dotenv import load_dotenv
import httpx

load_dotenv()

def find_page_in_database(db_id, query):
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
        print(f"Searching for '{query}' in database {db_id}...")
        response = http_client.post(f"{base_url}/databases/{db_id}/query")
        response.raise_for_status()
        results = response.json().get("results", [])
        
        found_page = None
        for page in results:
            props = page.get("properties", {})
            title = ""
            for p_name, p_val in props.items():
                if p_val.get("type") == "title" and p_val["title"]:
                    title = p_val["title"][0]["plain_text"]
                    break
            
            if query in title:
                found_page = {"id": page["id"], "title": title}
                break
        
        if found_page:
            print("FOUND!")
            print(f"Title: {found_page['title']}")
            print(f"ID: {found_page['id']}")
            return found_page["id"]
        else:
            print("NOT FOUND")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        http_client.close()

if __name__ == "__main__":
    TARGET_DB_ID = "34caad32-6752-8041-9295-fac5ed2ffdee"
    find_page_in_database(TARGET_DB_ID, "m20260422")
