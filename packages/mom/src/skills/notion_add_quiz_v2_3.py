import os
import requests
import time
from typing import List, Dict, Any

def add_notion_blocks(token, page_id, content_blocks):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    payload = { "children": content_blocks }
    response = requests.patch(url, json=payload, headers=headers, verify=False)
    return response.status_code, response.text

def create_toggle_and_children(token, page_id, question_text):
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    # 1. Create Toggle H4
    url_page = f"https://api.notion.com/v1/blocks/{page_id}/children"
    payload = {
        "children": [
            {
                "object": "block",
                "type": "heading_4",
                "heading_4": {
                    "rich_text": [{"type": "text", "text": {"content": question_text}}],
                    "is_toggleable": True
                }
            }
        ]
    }
    res = requests.patch(url_page, json=payload, headers=headers, verify=False)
    res.raise_for_status()
    toggle_id = res.json()["results"][0]["id"]
    
    # CRITICAL: Long sleep to avoid 400/404 errors due to Notion's eventual consistency
    time.sleep(1.5)
    
    # 2. Add Children (Callouts) to the Toggle
    url_toggle = f"https://api.notion.com/v1/blocks/{toggle_id}/children"
    children_payload = {
        "children": [
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "type": "emoji",
                    "icon": {"emoji": "✏️"},
                    "rich_text": [{"type": "text", "text": {"content": "我的答案：\n(請直接在此輸入答案，例如: C)"}}]
                }
            },
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "type": "emoji",
                    "icon": {"emoji": "🤖"},
                    "rich_text": [{"type": "text", "text": {"content": "批閱結果：(等待批閱...)"}}]
                }
            }
        ]
    }
    res_children = requests.patch(url_toggle, json=children_payload, headers=headers, verify=False)
    res_children.raise_for_status()
    return True

if __name__ == "__main__":
    token = os.getenv("NOTION_TOKEN")
    page_id = "34caad32-6752-8127-a846-eed9a69e0de5"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    clear_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    res_get = requests.get(clear_url, headers=headers, verify=False)
    blocks = res_get.json().get("results", [])
    for b in blocks:
        requests.patch(f"https://api.notion.com/v1/blocks/{b['id']}", json={"archived": True}, headers=headers, verify=False)

    header_blocks = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📅 AI 應用規劃師中級模擬練習 - 2026-04-27 (v2.3)"}}] }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": "本次測驗範圍：[科目1-AI相關技術應用] NLP 基礎與前處理\n\n💡 **操作指南：請點擊下方題目展開，在 ✏️ 區塊填入答案後告知小白批改！**"}}] }
        }
    ]
    add_notion_blocks(token, page_id, header_blocks)
    
    questions = [
        "1. 關於自然語言處理（NLP）的發展脈絡，下列敘述何者正確？\n(A) 規則式方法依賴大量語料訓練機率模型\n(B) 統計語言模型（如 N-gram）能有效捕捉長距離依賴\n(C) Transformer 透過自注意力機制解決了長距離依賴問題\n(D) 預訓練語言模型必須針對單一任務從零開始訓練",
        "2. 在 NLP 前處理中，「詞形還原」與「詞幹提取」的主要區別為何？\n(A) 詞幹提取依賴字典，語意保留較佳\n(B) 詞形還原還原為字典形式保留語意，詞幹提取快速裁剪詞尾\n(C) 詞幹提取僅用於中文，詞形還原僅用於英文\n(D) 兩者在功能上完全相同",
        "3. 關於 Word2Vec 的 CBOW 與 Skip-gram 兩種模型，下列分析何者正確？\n(A) CBOW 是以中心詞預測周圍上下文\n(B) Skip-gram 是以上下文預測中心詞\n(C) Skip-gram 對於低頻詞的捕捉能力通常更好\n(D) CBOW 訓練速度較慢但語意捕捉更深",
        "4. tf-idf 統計方法中，IDF 的主要目的為何？\n(A) 衡量單一文件中的詞頻\n(B) 衡量詞彙在整體語料庫中的罕見程度，降低常見詞權重\n(C) 將詞彙轉換為高維度向量\n(D) 捕捉詞彙之間的序列結構",
        "5. BERT 與 GPT 在 Transformer 的應用上最顯著的差異是什麼？\n(A) BERT 使用單向預測，GPT 使用雙向遮蔽\n(B) BERT 專精生成，GPT 專精理解\n(C) BERT 採用雙向編碼器理解上下文，GPT 採用單向自迴歸生成\n(D) BERT 計算資源需求遠低於 GPT",
        "6. 下列關於「語境型表示 (Contextual Representation)」的敘述何者正確？\n(A) 每個詞在所有語境中保持不變的向量\n(B) 向量會根據其所在句子或語境動態改變，可解決多義詞問題\n(C) Word2Vec 是典型的語境型表示方法\n(D) 語境型表示不需要大規模預訓練",
        "7. 在 NLP 前處理的「停用詞移除 (Stopword Removal)」中，下列敘述何者正確？\n(A) 必須在所有 NLP 任務中移除所有停用詞\n(B) 移除停用詞可降低資料維度，但可能影響對話生成的自然度\n(C) 停用詞是指具有高語義貢獻的關鍵詞\n(D) 停用詞移除是在分詞之前執行的步驟",
        "8. 關於 Transformer 的「自注意力機制 (Self-Attention)」，其核心價值在於？\n(A) 必須按順序逐字讀取序列\n(B) 能夠同時考慮整個輸入序列的所有詞，實現全局語境建模\n(C) 徹底取代了所有詞嵌入 (Word Embedding) 技術\n(D) 只能處理短句子，無法處理長距離依賴",
        "9. 下列哪一項是「分布式表示 (Distributed Representation)」的特點？\n(A) 每個詞被映射到一個獨立的、僅有一個維度為1的稀疏向量\n(B) 語意相近的詞會被映射到向量空間中的相近位置\n(C) 完全不考慮詞彙之間的關聯性\n(D) 僅能透過手動設計語法規則來實現",
        "10. 關於 ELMo 模型，下列敘述何者正確？\n(A) 它基於 Transformer 的雙向編碼器\n(B) 它基於雙向 LSTM (BiLSTM) 語言模型來產生語境敏感向量\n(C) 它無法處理多義詞問題\n(D) 它是第一個提出自注意力機制的模型"
    ]
    
    for q in questions:
        create_toggle_and_children(token, page_id, q)
    
    print("Successfully generated v2.3 Exam with 10 Questions, guaranteed Callouts and slower API calls.")
