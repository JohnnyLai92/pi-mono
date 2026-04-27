import os
import requests
from typing import List, Dict, Any

def add_notion_blocks(token, page_id, content_blocks):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    payload = {
        "children": content_blocks
    }
    response = requests.patch(url, json=payload, headers=headers, verify=False)
    return response.status_code, response.text

def generate_quiz_blocks():
    # The goal is to create a structure: 
    # Toggle H2 (Question) -> [Callout ✏️ (Answer), Callout 🤖 (Feedback)]
    # However, Notion API for adding children to a page ONLY allows adding top-level blocks.
    # To add children to a Toggle, we must:
    # 1. Create the Toggle H2 block.
    # 2. Get its ID.
    # 3. Call /blocks/{toggle_id}/children to add the Callouts.
    
    # For the initial page setup, we return only the Toggles.
    # The script will then handle the child addition.
    
    questions = [
        "1. 關於自然語言處理（NLP）的發展脈絡，下列敘述何者正確？\n(A) 規則式方法依賴大量語料訓練機率模型，且具高可解釋性\n(B) 統計語言模型（如 N-gram）能有效捕捉長距離的語言依賴性\n(C) Transformer 架構透過自注意力機制實現全局語境建模，解決了長距離依賴問題\n(D) 預訓練語言模型（如 BERT）必須針對單一任務從零開始訓練，無法進行微調",
        "2. 在 NLP 前處理中，「詞形還原 (Lemmatization)」與「詞幹提取 (Stemming)」的主要區別為何？\n(A) 詞幹提取依賴字典，語意保留較佳；詞形還原使用簡單裁剪\n(B) 詞形還原將單詞還原為字典形式，保留語意一致性；詞幹提取則快速裁剪詞尾\n(C) 詞幹提取僅用於中文斷詞，詞形還原僅用於英文\n(D) 兩者在功能上完全相同，僅在運算速度上有所差異",
        "3. 關於 Word2Vec 的 CBOW 與 Skip-gram 兩種模型，下列分析何者正確？\n(A) CBOW 是以中心詞預測周圍上下文詞彙\n(B) Skip-gram 是以上下文詞彙預測中心詞\n(C) Skip-gram 對於低頻詞的語意捕捉能力通常比 CBOW 更好\n(D) CBOW 的訓練速度較慢，但能比 Skip-gram 捕捉更深層的語意",
        "4. tf-idf 統計方法中，IDF (Inverse Document Frequency) 的主要目的為何？\n(A) 衡量單一文件中的詞頻\n(B) 衡量詞彙在整體語料庫中的罕見程度，以降低過於常見詞的權重\n(C) 將詞彙轉換為高維度向量\n(D) 捕捉詞彙之間的序列與語法結構",
        "5. BERT 與 GPT 在 Transformer 的應用上最顯著的差異是什麼？\n(A) BERT 使用單向自迴歸預測，GPT 使用雙向遮蔽語言模型\n(B) BERT 專精於文本生成，GPT 專精於上下文理解\n(C) BERT 採用雙向編碼器以理解上下文，GPT 採用單向自迴歸預測以生成文本\n(D) BERT 的計算資源需求遠低於 GPT"
    ]
    
    top_level_blocks = []
    # Add Header
    top_level_blocks.append({
        "object": "block",
        "type": "heading_2",
        "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📅 AI 應用規劃師中級模擬練習 - 2026-04-27 (v2.0)"}}] }
    })
    top_level_blocks.append({
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": "本次測驗範圍：[科目1-AI相關技術應用] NLP 基礎與前處理\n\n💡 **操作指南：請展開每題的摺疊標題，在 ✏️ 區塊內填入答案，完成後告知小白批改！**"}}] }
    })

    # We return the a list of question texts to be processed by the main loop
    return top_level_blocks, questions

def create_toggle_and_children(token, page_id, question_text):
    # 1. Create Toggle H2
    url_page = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    payload = {
        "children": [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": question_text}}],
                    "is_toggleable": True
                }
            }
        ]
    }
    res = requests.patch(url_page, json=payload, headers=headers, verify=False)
    res.raise_for_status()
    toggle_id = res.json()["results"][0]["id"]
    
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
                    "rich_text": [{"type": "text", "text": {"content": "我的答案："}}]
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
    requests.patch(url_toggle, json=children_payload, headers=headers, verify=False)
    return True

if __name__ == "__main__":
    token = os.getenv("NOTION_TOKEN")
    page_id = "34caad32-6752-8127-a846-eed9a69e0de5"
    
    # Clear page first
    clear_url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    res_get = requests.get(clear_url, headers=headers, verify=False)
    blocks = res_get.json().get("results", [])
    for b in blocks:
        requests.patch(f"https://api.notion.com/v1/blocks/{b['id']}", json={"archived": True}, headers=headers, verify=False)

    # Generate questions
    top_blocks, questions = generate_quiz_blocks()
    
    # Add header blocks
    add_notion_blocks(token, page_id, top_blocks)
    
    # Add each question with its children
    for q in questions:
        create_toggle_and_children(token, page_id, q)
    
    print("Exam generated successfully with Toggle+Callout structure.")
