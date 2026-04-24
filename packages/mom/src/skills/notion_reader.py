import os
import requests
from typing import List, Dict, Any, Optional

class NotionSkill:
    """
    Industrial-grade Notion API Skill for pi agent.
    """
    FINISHED_STATUSES = frozenset(["完成", "Done", "Completed", "已完成"])
    DEFAULT_TIMEOUT = 10

    def __init__(self):
        self.token = os.getenv("NOTION_TOKEN")
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        self.base_url = "https://api.notion.com/v1"
        
        # Use requests.Session for connection pooling and shared headers
        self._session = requests.Session()
        if self.token:
            self._session.headers.update({
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            })

    def _extract_title(self, properties: Dict[str, Any]) -> str:
        for prop_data in properties.values():
            if prop_data.get("type") == "title":
                title_list = prop_data.get("title", [])
                if title_list:
                    return title_list[0].get("plain_text", "Untitled")
        return "Untitled"

    def _extract_status(self, properties: Dict[str, Any]) -> str:
        for prop_data in properties.values():
            if prop_data.get("type") == "status":
                status_data = prop_data.get("status", {})
                return status_data.get("name", "Unknown")
        return "Unknown"

    def _paginate(self, url: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generic Notion API pagination handler."""
        results = []
        cursor = None
        while True:
            if cursor:
                payload["start_cursor"] = cursor
            
            try:
                response = self._session.post(url, json=payload, timeout=self.DEFAULT_TIMEOUT)
                response.raise_for_status()
                data = response.json()
                
                results.extend(data.get("results", []))
                if not data.get("has_more"):
                    break
                cursor = data.get("next_cursor")
            except Exception as e:
                # In a real scenario, we might want to raise this or log it
                # For this skill, we return what we have so far and append the error
                results.append({"error": f"Pagination failed: {str(e)}"})
                break
        return results

    def list_pages(self) -> List[Dict[str, Any]]:
        """Lists all pages using the search API (General Search)."""
        if not self.token:
            return [{"error": "NOTION_TOKEN is not set in environment variables."}]
        
        url = f"{self.base_url}/search"
        payload = {}
        
        try:
            all_results = self._paginate(url, payload)
            pages = []
            for obj in all_results:
                if "error" in obj:
                    pages.append(obj)
                    continue
                if obj.get("object") == "page":
                    title = self._extract_title(obj.get("properties", {}))
                    pages.append({
                        "id": obj["id"], 
                        "title": title, 
                        "object": obj["object"], 
                        "url": obj.get("url", "")
                    })
            return pages
        except Exception as e:
            return [{"error": f"API Request failed: {str(e)}"}]

    def get_unfinished_tasks(self) -> List[Dict[str, Any]]:
        """
        Retrieves unfinished tasks from the target database, filtered client-side.
        """
        if not self.token:
            return [{"error": "NOTION_TOKEN is not set in environment variables."}]
        if not self.database_id:
            return [{"error": "NOTION_DATABASE_ID is not set in environment variables."}]

        url = f"{self.base_url}/databases/{self.database_id}/query"
        all_results = self._paginate(url, {})

        unfinished = []
        for obj in all_results:
            if "error" in obj:
                unfinished.append(obj)
                continue
            if obj.get("object") == "page":
                props = obj.get("properties", {})
                title = self._extract_title(props)
                status = self._extract_status(props)
                if status not in self.FINISHED_STATUSES:
                    unfinished.append({
                        "id": obj["id"], 
                        "title": title, 
                        "status": status, 
                        "url": obj.get("url", "")
                    })
        
        return unfinished
