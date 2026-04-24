import os
from packages.mom.src.skills.notion_reader import NotionSkill
from dotenv import load_dotenv

load_dotenv()

def main():
    skill = NotionSkill()
    print("🚀 Calling upgraded NotionSkill (Industrial Grade)...")
    tasks = skill.get_unfinished_tasks()
    
    if isinstance(tasks, list) and len(tasks) > 0 and "error" in tasks[0]:
        print(f"❌ Error occurred: {tasks[0]['error']}")
    elif not tasks:
        print("✅ No unfinished tasks found.")
    else:
        print(f"📋 Found {len(tasks)} unfinished tasks:")
        for task in tasks:
            if "error" in task:
                print(f"⚠️ {task['error']}")
                continue
            print(f"- {task.get('title')} [Status: {task.get('status')}]")
            print(f"  🔗 URL: {task.get('url')}")

if __name__ == "__main__":
    main()
