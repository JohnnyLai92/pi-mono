import os
from dotenv import load_dotenv
from packages.mom.src.skills.notion_reader import NotionSkill
import json

def main():
    load_dotenv()
    skill = NotionSkill()
    result = skill.create_task(title="回Peter CYG分文優化的email")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
