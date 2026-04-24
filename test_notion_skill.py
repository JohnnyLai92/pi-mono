import os
from packages.mom.src.skills.notion_reader import NotionSkill

# 手動模擬載入環境變數 (假設您已經在系統中設定好，或者我們在這裡模擬)
# 在真實環境中，這應該由 pi 的啟動流程處理
os.environ["NOTION_TOKEN"] = "dummy_token_for_syntax_check"

def test_skill():
    print("Starting NotionSkill test...")
    skill = NotionSkill()
    result = skill.list_pages()
    print(f"Result: {result}")

if __name__ == "__main__":
    test_skill()
