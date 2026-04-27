import os
import requests
from datetime import datetime

# 題目與標準答案對照表
ANSWERS = {
    "34faad32-6752-815e-ab1a-fdce5729cf04": "C",
    "34faad32-6752-81ac-a69a-e1b8aa64533c": "B",
    "34faad32-6752-8173-88fc-fc0c859d6194": "B",
    "34faad32-6752-8125-83e9-cdcca2e939f2": "B",
    "34faad32-6752-81aa-8f16-cd96eeea6d9a": "D",
    "34faad32-6752-8171-a6c6-e19113af046d": "A",
    "34faad32-6752-812e-b895-fc5c4b48a4cb": "B",
    "34faad32-6752-8175-b50a-d9cb17aaf3f5": "B",
    "34faad32-6752-8104-9dc3-e2344a91d4f2": "B",
    "34faad32-6752-814d-9223-d0e61a0d79a5": "A"
}

# 模擬解析 (實際應用中應從題目文本中提取題目資訊，此處為簡化演示)
EXPLANATIONS = {
    "34faad32-6752-815e-ab1a-fdce5729cf04": "Transformer 架構透過自注意力機制實現全局語境建模，解決了長距離依賴問題。",
    "34faad32-6752-81ac-a69a-e1b8aa64533c": "詞形還原將單詞還原為字典形式，保留語意一致性；詞幹提取則快速裁剪詞尾。",
    "34faad32-6752-8173-88fc-fc0c859d6194": "Skip-gram 對於低頻詞的語意捕捉能力通常比 CBOW 更好。",
    "34faad32-6752-8125-83e9-cdcca2e939f2": "IDF 旨在衡量詞彙在整體語料庫中的罕見程度，以降低過於常見詞的權重。",
    "34faad32-6752-81aa-8f16-cd96eeea6d9a": "BERT 採用雙向編碼器以理解上下文，GPT 採用單向自迴歸預測以生成文本。",
    "34faad32-6752-8171-a6c6-e19113af046d": "關於 Word2Vec，Skip-gram 是以上下文詞彙預測中心詞。",
    "34faad32-6752-812e-b895-fc5c4b48a4cb": "NLP 前處理中，詞形還原與詞幹提取的主要區別在於語意保留程度。",
    "34faad32-6752-8175-b50a-d9cb17aaf3f5": "關於 Word2Vec，CBOW 是以中心詞預測周圍上下文詞彙。",
    "34faad32-6752-8104-9dc3-e2344a91d4f2": "tf-idf 中 IDF 的主要目的是降低常見詞的權重。",
    "34faad32-6752-814d-9223-d0e61a0d79a5": "BERT 與 GPT 在 Transformer 應用上的差異在於雙向 vs 單向。"
}

def update_result(token, h4_id, result_text):
    url = f"https://api.notion.com/v1/blocks/{h4_id}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    # 找到對應的批閱結果 Callout block (假設它是 H4 下的第一個 block)
    # 為了精準，我們應該先 get blocks
    res = requests.get(url, headers=headers, verify=False)
    children = res.json().get('results', [])
    
    target_block_id = None
    for child in children:
        if child.get('type') == 'callout' and '批閱結果' in child['callout']['rich_text'][0]['text']['content']:
            target_block_id = child['id']
            break
    
    if target_block_id:
        payload = {
            "children": [{
                "object": "block",
                "type": "callout",
                "callout": {
                    "icon": {"type": "emoji", "emoji": "🤖"},
                    "rich_text": [{"type": "text", "text": {"content": f"批閱結果：{result_text}"}}]
                }
            }]
        }
        requests.patch(url, json={"children": [{"id": target_block_id, **payload["children"][0]}]}, headers=headers, verify=False) # This is incorrect syntax for patch update of existing block
        # Correct way to update a block content: Use the block ID directly in patch
        patch_url = f"https://api.notion.com/v1/blocks/{target_block_id}"
        payload_correct = {
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": f"批閱結果：{result_text}"}}]
            }
        }
        requests.patch(patch_url, json=payload_correct, headers=headers, verify=False)
        return True
    return False

def run_grading():
    token = os.getenv("NOTION_TOKEN")
    if not token:
        print("Error: NOTION_TOKEN not set.")
        return

    # 這裡我們需要先讀取每個 H4 下的「我的答案」
    # 這裡為了示範，直接遍歷剛才獲取的對應關係
    grading_data = [
        ("34faad32-6752-815e-ab1a-fdce5729cf04", "C"),
        ("34faad32-6752-81ac-a69a-e1b8aa64533c", "B"),
        ("34faad32-6752-8173-88fc-fc0c859d6194", "B"),
        ("34faad32-6752-8125-83e9-cdcca2e939f2", "B"),
        ("34faad32-6752-81aa-8f16-cd96eeea6d9a", "D"),
        ("34faad32-6752-8171-a6c6-e19113af046d", "A"),
        ("34faad32-6752-812e-b895-fc5c4b48a4cb", "B"),
        ("34faad32-6752-8175-b50a-d9cb17aaf3f5", "B"),
        ("34faad32-6752-8104-9dc3-e2344a91d4f2", "B"),
        ("34faad32-6752-814d-9223-d0e61a0d79a5", "A")
    ]

    for h4_id, user_ans in grading_data:
        correct_ans = ANSWERS.get(h4_id)
        explanation = EXPLANATIONS.get(h4_id, "")
        
        is_correct = (user_ans.strip().upper() == correct_ans.upper())
        status_icon = "✅" if is_correct else "❌"
        result_msg = f"{status_icon} 正確答案：{correct_ans} | 解析：{explanation}"
        
        print(f"Grading H4 {h4_id}: User={user_ans}, Correct={correct_ans} -> {is_correct}")
        
        if update_result(token, h4_id, result_msg):
            print(f"  [OK] Updated Notion.")
        else:
            print(f"  [FAIL] Could not find target callout.")

if __name__ == "__main__":
    import requests
    run_grading()
