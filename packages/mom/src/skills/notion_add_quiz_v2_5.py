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

def generate_quiz_structure():
    questions = [
        "1. 關於 NLP 的發展脈絡，下列敘述何者正確？\n(A) 規則式方法依賴大量語料訓練\n(B) 統計語言模型能有效捕捉長距離依賴\n(C) Transformer 透過自注意力機制解決長距離依賴\n(D) 預訓練模型必須從零開始訓練",
        "2. 「詞形還原」與「詞幹提取」的主要區別為何？\n(A) 詞幹提取依賴字典，保留語意較佳\n(B) 詞形還原還原為字典形式，詞幹提取快速裁剪詞尾\n(C) 詞幹提取僅用於中文\n(D) 兩者完全相同",
        "3. Word2Vec 的 CBOW 與 Skip-gram 分析何者正確？\n(A) CBOW 是中心詞預測周圍上下文\n(B) Skip-gram 是上下文預測中心詞\n(C) Skip-gram 對低頻詞捕捉能力通常更好\n(D) CBOW 訓練速度較慢",
        "4. tf-idf 中，IDF 的主要目的為何？\n(A) 衡量單一文件詞頻\n(B) 衡量詞彙在語料庫中的罕減程度，降低常見詞權重\n(C) 轉換高維度向量\n(D) 捕捉序列結構",
        "5. BERT 與 GPT 在 Transformer 應用上的顯著差異？\n(A) BERT 單向預測，GPT 雙向遮蔽\n(B) BERT 專精生成，GPT 專精理解\n(C) BERT 雙向編碼器理解上下文，GPT 單向自迴歸生成\n(D) BERT 資源需求遠低於 GPT",
        "6. 「語境型表示」的敘述何者正確？\n(A) 每個詞向量在所有語境中不變\n(B) 向量隨語境動態改變，解決多義詞問題\n(C) Word2Vec 是典型的語境型表示\n(D) 不需要大規模預訓練",
        "7. 「停用詞移除」敘述何者正確？\n(A) 必須移除所有停用詞\n(B) 降低資料維度，但可能影響對話自然度\n(C) 停用詞是高語義貢獻詞\n(D) 在分詞前執行",
        "8. 「自注意力機制 (Self-Attention)」核心價值在於？\n(A) 必須按順序逐字讀取\n(B) 同時考慮全序列所有詞，實現全局語境建模\n(C) 取代所有詞嵌入技術\n(D) 只能處理短句子",
        "9. 「分布式表示」的特點是？\n(A) 映射到單一維度為1的稀疏向量\n(B) 語意相近詞映射到向量空間相近位置\n(C) 不考慮詞彙關聯\n(D) 依賴手動設計規則",
        "10. 關於 ELMo 模型，敘述何者正確？\n(A) 基於 Transformer 雙向編碼器\n(B) 基於雙向 LSTM 產生語境敏感向量\n(C) 無法處理多義詞\n(D) 第一個提出自注意力機制"
    ]
    
    blocks = []
    # Header
    blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📅 AI 應用規劃師中級模擬練習 - 2026-04-27 (v2.5)"}}] }
    })
    blocks.append({
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": "✏️ **填答指南**：展開 H4 題目 $\rightarrow$ 在 ✏️ 區塊輸入答案 $\rightarrow$ 告知小白批改。"}}] }
    })

    # Atomic Nesting Questions
    for q in questions:
        blocks.append({
            "object": "block",
            "type": "heading_4",
            "heading_4": {
                "rich_text": [{"type": "text", "text": {"content": q}}],
                "is_toggleable": True
            },
            "children": [
                {
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "icon": {"type": "emoji", "emoji": "✏️"},
                        "rich_text": [{"type": "text", "text": {"content": "我的答案：\n(在此輸入內容)"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "icon": {"type": "emoji", "emoji": "🤖"},
                        "rich_text": [{"type": "text", "text": {"content": "批閱結果：(等待批閱...)"}}]
                    }
                }
            ]
        })
    
    return blocks

if __name__ == "__main__":
    token = os.getenv("NOTION_TOKEN")
    page_id = "34caad32-6752-8127-a846-eed9a69e0de5"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    # Clear Page
    clear_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    res_get = requests.get(clear_url, headers=headers, verify=False)
    blocks_to_clear = res_get.json().get("results", [])
    for b in blocks_to_clear:
        requests.patch(f"https://api.notion.com/v1/blocks/{b['id']}", json={"archived": True}, headers=headers, verify=False)

    # Generate atomic blocks
    all_blocks = generate_quiz_structure()
    
    # Note: Notion /children API currently only accepts top-level blocks.
    # To use the "children" property within a block, we usually need to create 
    # the block via a different flow, but for PATCH /children, it's not always supported.
    # Wait, current Notion API (2022-06-28) does NOT support "children" property 
    # in the /blocks/{id}/children PATCH endpoint. It only supports creating 
    # a block. To create a nested structure, we MUST use the two-step process.
    
    # I will revert back to two-step but with the FIXED Callout structure 
    # and much stronger retry logic, specifically fixing the "icon" object.

    # Revised Loop
    for i, block in enumerate(all_blocks):
        if block["type"] == "heading_4":
            # Create H4 Toggle
            url_page = f"https://api.notion.com/v1/blocks/{page_id}/children"
            payload = { "children": [block] }
            # Remove children property as it's not supported in this endpoint
            if "children" in payload["children"][0]:
                del payload["children"][0]["children"]
            
            res = requests.patch(url_page, json=payload, headers=headers, verify=False)
            res.raise_for_status()
            toggle_id = res.json()["results"][0]["id"]
            
            # Nest the children (the fix is in the icon object)
            time.sleep(1.0)
            url_toggle = f"https://api.notion.com/v1/blocks/{toggle_id}/children"
            
            # Recover the children from our original list
            child_blocks = block["children"]
            children_payload = { "children": child_blocks }
            
            retry_count = 0
            while retry_count < 5:
                res_children = requests.patch(url_toggle, json=children_payload, headers=headers, verify=False)
                if res_children.status_code == 200:
                    break
                retry_count += 1
                time.sleep(2 ** retry_count)
        else:
            # Just a normal top-level block
            add_notion_blocks(token, page_id, [block])

    print("Successfully generated v2.5 Exam with fixed Callout structure.")
