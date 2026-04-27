import os
import requests

QUIZ_DATA = [
    {"q": "關於自然語言處理（NLP）的發展脈絡，下列敘述何者正確？", "options": ["(A) 規則式方法依賴大量語料訓練機率模型，且具高可解釋性", "(B) 統計語言模型（如 N-gram）能有效捕捉長距離的語言依賴性", "(C) Transformer 架構透過自注意力機制實現全局語境建模，解決了長距離依賴問題", "(D) 預訓練語言模型（如 BERT）必須針對單一任務從零開始訓練，無法進行微調"]},
    {"q": "在 NLP 前處理中，「詞形還原 (Lemmatization)」與「詞幹提取 (Stemming)」的主要區別為何？", "options": ["(A) 詞幹提取依賴字典，語意保留較佳；詞形還原使用簡單裁剪", "(B) 詞形還原將單詞還原為字典形式，保留語意一致性；詞幹提取則快速裁剪詞尾", "(C) 詞幹提取僅用於中文斷詞，詞形還原僅用於英文", "(D) 兩者在功能上完全相同，僅在運算速度上有所差異"]},
    {"q": "關於 Word2Vec 的 CBOW 與 Skip-gram 兩種模型，下列分析何者正確？", "options": ["(A) CBOW 是以中心詞預測周圍上下文詞彙", "(B) Skip-gram 是以上下文詞彙預測中心詞", "(C) Skip-gram 對於低頻詞的語意捕捉能力通常比 CBOW 更好", "(D) CBOW 的訓練速度較慢，但能比 Skip-gram 捕捉更深層的語意"]},
    {"q": "tf-idf 統計方法中，IDF (Inverse Document Frequency) 的主要目的為何？", "options": ["(A) 衡量單一文件中的詞頻", "(B) 衡量詞彙在整體語料庫中的罕見程度，以降低過於常見詞的權重", "(C) 將詞彙轉換為高維度向量", "(D) 捕捉詞彙之間的序列與語法結構"]},
    {"q": "BERT 與 GPT 在 Transformer 的應用上最顯著的差異是什麼？", "options": ["(A) BERT 使用單向自迴歸預測，GPT 使用雙向遮蔽語言模型", "(B) BERT 專精於文本生成，GPT 專精於上下文理解", "(C) BERT 採用雙向編碼器以理解上下文，GPT 採用單向自迴歸預測以生成文本", "(D) BERT 的計算資源需求遠低於 GPT"]},
    {"q": "關於 Transformer 的 Self-Attention 機制，下列敘述何者正確？", "options": ["(A) 它僅能處理固定長度的輸入序列", "(B) 透過 Query, Key, Value 三個向量計算權重，實現動態關注", "(C) 必須依賴 RNN 的遞迴結構才能運作", "(D) 只能處理單一語言的文本"]},
    {"q": "在 LLM 微調中，LoRA (Low-Rank Adaptation) 的核心邏輯是什麼？", "options": ["(A) 重新訓練模型的所有權重", "(B) 凍結原權重，僅更新兩個低秩分解矩陣，減少參數更新量", "(C) 增加模型的層數以提升表現", "(D) 僅對輸出層進行權重更新"]},
    {"q": "關於 RAG (Retrieval-Augmented Generation) 的流程，下列順序何者正確？", "options": ["(A) 生成答案 -> 檢索資料 -> 建立索引", "(B) 建立索引 -> 檢索資料 -> 生成答案", "(C) 檢索資料 -> 生成答案 -> 建立索引", "(D) 生成答案 -> 建立索引 -> 檢索資料"]},
    {"q": "LLM 中的 Temperature 參數主要影響什麼？", "options": ["(A) 模型的訓練速度", "(B) 文本生成的隨機性與創造力", "(C) 模型能處理的最大 Token 長度", "(D) 答案的正確率直接相關"]},
    {"q": "關於 Prompt Engineering 中的 Few-Shot Prompting，其定義是什麼？", "options": ["(A) 不提供任何範例，直接要求結果", "(B) 提供一個範例後要求結果", "(C) 提供少量的範例讓模型學習任務模式後再要求結果", "(D) 讓模型在數百萬筆資料上進行預訓練"]}
]

def clear_page(session, page_id, headers):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    res = session.get(url, headers=headers)
    if res.status_code == 200:
        blocks = res.json().get("results", [])
        for b in blocks:
            session.patch(f"https://api.notion.com/v1/blocks/{b['id']}", json={"archived": True}, headers=headers)

def run():
    token = os.getenv("NOTION_TOKEN")
    page_id = "34caad32-6752-8127-a846-eed9a69e0de5"
    headers = {"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
    session = requests.Session()
    session.verify = False
    
    clear_page(session, page_id, headers)
    
    append_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    h2_res = session.patch(append_url, json={
        "children": [{
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📅 AI 應用規劃師中級模擬練習 (2026-04-27 v2)"}}], "is_toggleable": True}
        }]
    }, headers=headers)
    
    if h2_res.status_code == 200:
        h2_id = h2_res.json()["results"][0]["id"]
        h2_children_url = f"https://api.notion.com/v1/blocks/{h2_id}/children"
        
        for i, data in enumerate(QUIZ_DATA):
            q_text = f"題目 {i+1}：{data['q']}"
            h4_res = session.patch(h2_children_url, json={
                "children": [{
                    "object": "block",
                    "type": "heading_4",
                    "heading_4": {"rich_text": [{"type": "text", "text": {"content": q_text}}], "is_toggleable": True}
                }]
            }, headers=headers)
            
            if h4_res.status_code == 200:
                h4_id = h4_res.json()["results"][0]["id"]
                h4_children_url = f"https://api.notion.com/v1/blocks/{h4_id}/children"
                
                option_blocks = []
                for opt in data["options"]:
                    option_blocks.append({"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": opt}}]}})
                option_blocks.append({"object": "block", "type": "callout", "callout": {"icon": {"type": "emoji", "emoji": "✏️"}, "rich_text": [{"type": "text", "text": {"content": "我的答案：(在此輸入)"}}]}})
                option_blocks.append({"object": "block", "type": "callout", "callout": {"icon": {"type": "emoji", "emoji": "🤖"}, "rich_text": [{"type": "text", "text": {"content": "批閱結果：(等待批閱...)"}}]}})
                
                session.patch(h4_children_url, json={"children": option_blocks}, headers=headers)

    print("✅ 頂層 Toggle 結構重建完成！")

if __name__ == "__main__":
    run()
