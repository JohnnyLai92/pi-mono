import os
from dotenv import load_dotenv
from packages.mom.src.skills.notion_reader import NotionSkill
import json

def main():
    load_dotenv()
    skill = NotionSkill()
    schema = skill.get_database_schema()
    print(json.dumps(schema, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
