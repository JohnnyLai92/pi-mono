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
        print(f"正在搜尋包含 '{query}' 的內容...\n")
        search_payload = {"query": query}
        response = http_client.post(f"{base_url}/search", json=search_payload)
        response.raise_for_status()
        
        results = response.json().get("results", [])
        
        if not results:
            print("❌ 未找到任何匹配的結果。")
            return

        print(f"🔍 找到 {len(results)} 個相關項目：\n")
        for i, item in enumerate(results):
            obj_type = item.get("object")
            item_id = item.get("id")
            
            # 嘗試取得標題
            title = "未知標題"
            if obj_type == "page":
                # 頁面標題在 properties 中
                props = item.get("properties", {})
                for p_name, p_val in props.items():
                    if p_val.get("type") == "title" and p_val["title"]:
                        title = p_val["title"][0]["plain_text"]
                        break
            elif obj_type == "database":
                # 資料庫標題在 title 屬性中
                title = item.get("title", "未知資料庫")

            print(f"{i+1}. [{obj_type.upper()}] {title}")
            print(f"   ID: {item_id}")
            print("-" * 30)

    except Exception as e:
        print(f"❌ 搜尋時發生錯誤: {e}")
    finally:
        http_client.close()

if __name__ == "__main__":
    search_meetings("會議")
