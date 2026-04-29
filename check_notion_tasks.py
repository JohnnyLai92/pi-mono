import os
import sys
from packages.mom.src.skills.notion_reader import NotionSkill

def main():
    # 確保環境變數已讀取 (雖然在 shell 中已經有了，但在 script 裡保險起見)
    # 但通常 printenv 看到的變數在子進程中也會存在
    
    skill = NotionSkill()
    tasks = skill.get_unfinished_tasks()
    
    if not tasks:
        print("目前沒有未完成的工作項目。")
        return

    if isinstance(tasks, list) and len(tasks) > 0 and "error" in tasks[0]:
        print(f"錯誤: {tasks[0]['error']}")
        return

    print("--- Notion 未完成工作清單 ---")
    for i, task in enumerate(tasks, 1):
        status = task.get('status', '未知')
        print(f"{i}. [{status}] {task['title']} (ID: {task['id']})")
        print(f"   連結: {task['url']}")

if __name__ == "__main__":
    main()
