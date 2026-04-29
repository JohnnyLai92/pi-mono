import os
from dotenv import load_dotenv
from packages.mom.src.skills.notion_reader import NotionSkill
import json

def main():
    load_dotenv()
    skill = NotionSkill()
    page_id = "350aad32-6752-819b-b23c-e24cc76e79c1"
    
    content = [
        ("### 📋 分類問題分析記錄 (來自今日 STM)", "heading_3"),
        ("重要決策：", "paragraph"),
        ("- 訓練資料集 CYG1108.json 確認需進行 Relabeling (重新標註) 才能投入訓練", "bulleted_list_item"),
        ("關鍵發現：", "paragraph"),
        ("- 新舊文件分類邏輯根本分歧：CYG20260428 (主旨內容性質) vs CYG1108 (來文機關/文號)", "bulleted_list_item"),
        ("- 三大標籤雜訊問題：1. 性質與主旨不符 2. 依賴來文單位 3. 性質標籤與業務標籤混用", "bulleted_list_item"),
        ("- 排除 X01~X06 後仍有大量衝突 (如 TS 觀光誤標營業類、CA 民政誤標績效獎勵類)", "bulleted_list_item"),
        ("待辦事項：", "paragraph"),
        ("- 對 CYG1108.json 進行 Relabeling, 修正標籤雜訊", "bulleted_list_item"),
        ("- 統一新舊資料集的分類邏輯 (建議全面採用主旨內容導向)", "bulleted_list_item"),
        ("- 重新訓練模型前先驗證資料品質", "bulleted_list_item"),
    ]
    
    for text, block_type in content:
        res = skill.append_text_to_page(page_id, text, block_type)
        if "error" in res:
            print(f"Error adding '{text}': {res['error']}")
        else:
            print(f"Added: {text}")

if __name__ == "__main__":
    main()
