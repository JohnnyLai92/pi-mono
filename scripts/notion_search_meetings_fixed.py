import os
from dotenv import load_dotenv
import httpx

load_dotenv()

def search_meetings(query):
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
        print(f"Searching for: {query}")
        search_payload = {"query": query}
        response = http_client.post(f"{base_url}/search", json=search_payload)
        response.raise_for_status()
        
        results = response.json().get("results", [])
        
        if not results:
            print("No results found.")
            return

        print(f"Found {len(results)} items:\n")
        for i, item in enumerate(results):
            obj_type = item.get("object")
            item_id = item.get("id")
            
            title = "Untitled"
            if obj_type == "page":
                props = item.get("properties", {})
                for p_name, p_val in props.items():
                    if p_val.get("type") == "title" and p_val["title"]:
                        title = p_val["title"][0]["plain_text"]
                        break
            elif obj_type == "database":
                title = item.get("title", "Untitled Database")

            print(f"{i+1}. [{obj_type.upper()}] {title}")
            print(f"   ID: {item_id}")
            print("-" * 30)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        http_client.close()

if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "會議"
    search_meetings(q)
EOF
