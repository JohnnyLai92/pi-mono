from packages.mom.src.skills.notion_reader import NotionSkill
import json

def main():
    skill = NotionSkill()
    tasks = skill.get_unfinished_tasks()
    print(json.dumps(tasks, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
