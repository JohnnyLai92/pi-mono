import os
import requests
from typing import List, Dict, Any

class NotionSkill:
    """
    Notion API Skill for pi agent.
    """
    def __init__(self):
        # 根據您的提示，變數名稱為 NOTION_TOKEN
        self.token = os.getenv("NOTION_TOKEN")
        self.base_url = "https://api.notion.com/v1"

    def list_pages(self) -> List[Dict[str, Any]]:
        """
        列出 Notion 中的所有頁面 (使用 Search API)。
        """
        if not self.token:
            return [{"error": "NOTION_TOKEN is not set in environment variables."}]

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

        try:
            # 使用 Search API 來尋找所有頁面與資料庫
            # 必須傳送一個空的 JSON body ({}) 否則 Notion 會報錯
            response = requests.post(f"{self.base_url}/search", headers=headers, json={})
            response.raise_for_status()
            data = response.json()
            
            pages = []
            for obj in data.get("results", []):
                if obj["object"] == "page":
                    # 嘗試提取標題 (Notion 的標題結構較複雜，這裡先抓取 ID)
                    pages.append({
                        "id": obj["id"],
                        "object": obj["object"],
                        "url": obj.get("url", "")
                    })
            return pages
        except Exception as e:
            return [{"error": f"API Request failed: {str(e)}"}]

if __name__ == "__main__":
    # 測試用
    skill = NotionSkill()
    print(skill.list_pages())
