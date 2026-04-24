import os
import requests
from typing import List, Dict, Any

class NotionSkill:
    """
    Notion API Skill for pi agent.
    """
    def __init__(self):
        self.token = os.getenv("NOTION_TOKEN")
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        self.base_url = "https://api.notion.com/v1"

    def _extract_title(self, properties: Dict[str, Any]) -> str:
        for prop_name, prop_data in properties.items():
            if prop_data.get("type") == "title":
                title_list = prop_data.get("title", [])
                if title_list:
                    return title_list[0].get("plain_text", "Untitled")
        return "Untitled"

    def _extract_status(self, properties: Dict[str, Any]) -> str:
        for prop_name, prop_data in properties.items():
            if prop_data.get("type") == "status":
                status_data = prop_data.get("status", {})
                return status_data.get("name", "Unknown")
        return "Unknown"

    def list_pages(self) -> List[Dict[str, Any]]:
        if not self.token:
            return [{"error": "NOTION_TOKEN is not set in environment variables."}]
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(f"{self.base_url}/search", headers=headers, json={})
            response.raise_for_status()
            data = response.json()
            pages = []
            for obj in data.get("results", []):
                if obj["object"] == "page":
                    title = self._extract_title(obj.get("properties", {}))
                    pages.append({"id": obj["id"], "title": title, "object": obj["object"], "url": obj.get("url", "")})
            return pages
        except Exception as e:
            return [{"error": f"API Request failed: {str(e)}"}]

    def get_unfinished_tasks(self) -> List[Dict[str, Any]]:
        if not self.token:
            return [{"error": "NOTION_TOKEN is not set in environment variables."}]
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(f"{self.base_url}/search", headers=headers, json={})
            response.raise_for_status()
            data = response.json()
            unfinished = []
            finished_keywords = ["完成", "Done", "Completed", "已完成"]
            for obj in data.get("results", []):
                if obj["object"] == "page":
                    props = obj.get("properties", {})
                    title = self._extract_title(props)
                    status = self._extract_status(props)
                    if status not in finished_keywords:
                        unfinished.append({"id": obj["id"], "title": title, "status": status, "url": obj.get("url", "")})
            return unfinished
        except Exception as e:
            return [{"error": f"Failed to filter tasks: {str(e)}"}]
