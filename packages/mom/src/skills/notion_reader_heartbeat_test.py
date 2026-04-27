import os
import requests
from datetime import datetime
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
        
        self._session = requests.Session()
        self._session.verify = False
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
                results.append({"error": f"Pagination failed: {str(e)}"})
                break
        return results

    def update_heartbeat(self, page_id: str, timestamp: str):
        if not self.token:
            return {"error": "NOTION_TOKEN is not set."}
        url = f"{self.base_url}/pages/{page_id}"
        
        # Test different property types for '說明' (rich_text vs text)
        # Standard for Notion 'Text' property is rich_text
        payload = {
            "properties": {
                "說明": {
                    "rich_text": [{"text": {"content": f"上次小白登入時間：{timestamp}"}}]
                }
            }
        }
        
        try:
            response = self._session.patch(url, json=payload, timeout=self.DEFAULT_TIMEOUT)
            if response.status_code == 200:
                return {"status": "success"}
            
            # If rich_text fails, let's logs the error details for debugging
            return {"error": f"Heartbeat update failed: {response.status_code} {response.text}"}
        except Exception as e:
            return {"error": f"Heartbeat update failed: {str(e)}"}

    def get_unfinished_tasks(self) -> List[Dict[str, Any]]:
        if not self.token:
            return [{"error": "NOTION_TOKEN is not set."}]
        if not self.database_id:
            return [{"error": "NOTION_DATABASE_ID is not set."}]
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

if __name__ == "__main__":
    import sys
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            pass

    skill = NotionSkill()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    tasks = skill.get_unfinished_tasks()
    if tasks and "error" not in tasks[0]:
        target_page_id = tasks[0]["id"]
        print(f"Updating heartbeat for page: {target_page_id}")
        result = skill.update_heartbeat(target_page_id, now)
        print(result)
    else:
        print("No valid tasks found to update heartbeat.")
