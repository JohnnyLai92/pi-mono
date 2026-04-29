import os
import sys
import requests

# 強制將當前目錄與 mom 模組路徑加入 sys.path
sys.path.append(os.getcwd())

try:
    from packages.mom.src.skills.notion_reader import NotionSkill
    print("✅ Module Import: Success")
except Exception as e:
    print(f"❌ Module Import: Failed - {str(e)}")
    sys.exit(1)

def test_connection():
    print("🚀 Starting Notion Connection Test...")
    skill = NotionSkill()
    
    # 測試 1: 檢查 Token
    if not skill.token or not skill.database_id:
        print("❌ Environment Variables: NOTION_TOKEN or NOTION_DATABASE_ID missing")
        return

    # 測試 2: 嘗試獲取資料庫 Schema (這是最基本的讀取操作)
    print("📡 Attempting to fetch database schema...")
    schema = skill.get_database_schema()
    
    if "error" in schema:
        print(f"❌ API Connection: Failed - {schema['error']}")
    else:
        print("✅ API Connection: Success! Database schema retrieved.")
        # 打印出資料庫名稱或屬性數量以證明連線成功
        props = schema.get("properties", {})
        print(f"📊 Database Info: Found {len(props)} properties in the database.")

if __name__ == "__main__":
    test_connection()
