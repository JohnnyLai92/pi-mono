import os
import re
import requests

# 題目與標準答案對照表
ANSWERS_MAP = [
    {"correct": "C", "explanation": "Transformer 架構透過自注意力機制實現全局語境建模，解決了長距離依賴問題。"},
    {"correct": "B", "explanation": "詞形還原將單詞還原為字典形式，保留語意一致性；詞幹提取則快速裁剪詞尾。"},
    {"correct": "B", "explanation": "Skip-gram 對於低頻詞的語意捕捉能力通常比 CBOW 更好。"},
    {"correct": "B", "explanation": "IDF 旨在衡量詞彙在整體語料庫中的罕見程度，以降低過於常見詞的權重。"},
    {"correct": "D", "explanation": "BERT 採用雙向編碼器以理解上下文，GPT 採用單向自迴歸預測以生成文本。"},
    {"correct": "A", "explanation": "關於 Word2Vec，Skip-gram 是以上下文詞彙預測中心詞。"},
    {"correct": "B", "explanation": "NLP 前處理中，詞形還原與詞幹提取的主要區別在於語意保留程度。"},
    {"correct": "B", "explanation": "關於 Word2Vec，CBOW 是以中心詞預測周圍上下文詞彙。"},
    {"correct": "B", "explanation": "tf-idf 中 IDF 的主要目的是降低常見詞的權重。"},
    {"correct": "A", "explanation": "BERT 與 GPT 在 Transformer 應用上的差異在於雙向 vs 單向。"}
]

def archive_block(session, block_id, headers):
    url = f"https://api.notion.com/v1/blocks/{block_id}"
    payload = {"archived": True}
    res = session.patch(url, json=payload, headers=headers)
    return res.status_code == 200

def run_final_fix():
    token = os.getenv("NOTION_TOKEN")
    page_id = "34caad32-6752-8127-a846-eed9a69e0de5"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    session = requests.Session()
    session.verify = False

    print(f"🧹 開始大掃除並重新批改: {page_id}")

    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    res = session.get(url, headers=headers)
    if res.status_code != 200:
        print("無法讀取頁面內容")
        return
    
    all_blocks = res.json().get("results", [])
    h4_blocks = [b for b in all_blocks if b["type"] == "heading_4"]
    print(f"找到 {len(h4_blocks)} 個題目區塊")

    questions_processed = 0

    for h4 in h4_blocks:
        if questions_processed >= len(ANSWERS_MAP):
            break
            
        h4_id = h4["id"]
        children_url = f"https://api.notion.com/v1/blocks/{h4_id}/children"
        child_res = session.get(children_url, headers=headers)
        if child_res.status_code != 200:
            continue
            
        children = child_res.json().get("results", [])
        
        ans_block = None
        result_blocks_to_delete = []
        
        for cb in children:
            if cb["type"] == "callout":
                content = ""
                if cb["callout"]["rich_text"]:
                    content = cb["callout"]["rich_text"][0]["text"]["content"]
                
                if "✏️" in content:
                    ans_block = cb
                elif "🤖" in content or "批閱結果" in content:
                    result_blocks_to_delete.append(cb["id"])
        
        for b_id in result_blocks_to_delete:
            archive_block(session, b_id, headers)
        
        if ans_block:
            raw_text = ans_block["callout"]["rich_text"][0]["text"]["content"]
            match = re.search(r"[A-Da-d]", raw_text)
            user_ans = match.group(0).upper() if match else "?"
            
            correct_info = ANSWERS_MAP[questions_processed]
            correct_ans = correct_info["correct"]
            explanation = correct_info["explanation"]
            
            is_correct = (user_ans == correct_ans)
            icon = "✅" if is_correct else "❌"
            result_text = f"{icon} 正確答案：{correct_ans} | 解析：{explanation}"
            
            append_url = f"https://api.notion.com/v1/blocks/{h4_id}/children"
            append_payload = {
                "children": [
                    {
                        "object": "block",
                        "type": "callout",
                        "callout": {
                            "icon": {"type": "emoji", "emoji": "🤖"},
                            "rich_text": [{"type": "text", "text": {"content": f"批閱結果：{result_text}"}}]
                        }
                    }
                ]
            }
            patch_res = session.patch(append_url, json=append_payload, headers=headers)
            
            if patch_res.status_code == 200:
                print(f"  [OK] 題號 {questions_processed+1}: 答案 {user_ans} -> {result_text}")
                questions_processed += 1
            else:
                print(f"  [ERROR] 題號 {questions_processed+1}: 寫入失敗")
        else:
            print(f"  [WARN] 題號 {questions_processed+1}: 找不到答案區塊 ✏️")

    print(f"\\n✨ 掃除並批改完成！共處理 {questions_processed} 題。")

if __name__ == "__main__":
    run_final_fix()
