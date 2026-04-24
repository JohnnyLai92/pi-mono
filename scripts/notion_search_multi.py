import os
from dotenv import load_dotenv
import httpx

load_dotenv()

def search_multiple(queries):
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

    for query in queries:
        print(f"\n--- Searching for: {query} ---")
        try:
            search_res = http_client.post(f"{base_url}/search", json={"query": query})
            search_res.raise_for_status()
            results = search_res.json().get("results", [])
            
            if not results:
                print(f"No results for '{query}'")
                continue

            for res in results:
                if res["object"] == "page":
                    props = res.get("properties", {})
                    title = "Untitled"
                    for p_name, p_val in props.items():
                        if p_val.get("type") == "title" and p_val["title"]:
                            title = p_val["title"][0]["plain_text"]
                            break
                    print(f"MATCH: [{res['id']}] {title}")
        except Exception as e:
            print(f"Error: {e}")
    http_client.close()

if __name__ == "__main__":
    # 同時搜尋使用者輸入的 20240422 和我們剛才建立的 20260424 (或是 20260422)
    search_multiple(["20240422", "20260422", "m20260424"])
