import os
import re
import requests

# 正確答案對照表 (根據題目順序)
ANSWERS_MAP = [
    {"correct": "C", "explanation": "Transformer 架構透過自注意力機制實現全局語境建模，解決了長距離依賴問題。"},
    {"correct": "B", "explanation": "詞形還原將單詞還原為字典形式，保留語意一致性；詞幹提取則快速裁剪詞尾。"},
    {"correct": "B", "explanation": "Skip-gram 對於低頻詞的語意捕捉能力通常比 CBOW 更好。"},
    {"correct": "B", "explanation": "IDF 旨在衡量詞彙在整體語料庫中的罕見程度，以降低過於常見詞的權重。"},
    {"correct": "D", "explanation": "BERT 採用雙向編碼器以理解上下文，GPT 採用單向自迴歸預測以生成文本。"},
    {"correct": "B", "explanation": "透過 Query, Key, Value 三個向量計算權重，實現動態關注。"},
    {"correct": "B", "explanation": "凍結原權重，僅更新兩個低秩分解矩陣，減少參數更新量。"},
    {"correct": "B", "explanation": "正確流程為：建立索引 -> 檢索資料 -> 生成答案。"},
    {"correct": "B", "explanation": "Temperature 影響機率分佈，進而影響文本生成的隨機性與創造力。"},
    {"correct": "C", "explanation": "Few-Shot Prompting 是指提供少量的範例讓模型學習任務模式後再要求結果。"}
]

def run_grading():
    token = os.getenv("NOTION_TOKEN")
    page_id = "34caad32-6752-8127-a846-eed9a69e0de5"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    session = requests.Session()
    session.verify = False

    print(f"🚀 開始執行高可靠度批改: {page_id}")

    # 1. 找到頂層第一個 Toggle (Heading 2)
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    res = session.get(url, headers=headers)
    if res.status_code != 200:
        print("無法讀取頁面")
        return
    
    top_blocks = res.json().get("results", [])
    top_toggle = next((b for b in top_blocks if b["type"] == "heading_2" and b["heading_2"].get("is_toggleable")), None)
    
    if not top_toggle:
        print("❌ 找不到頂層 Toggle (Heading 2)")
        return
    
    # 2. 進入頂層 Toggle 找到所有題目 (Heading 4)
    h2_children_url = f"https://api.notion.com/v1/blocks/{top_toggle['id']}/children"
    h2_res = session.get(h2_children_url, headers=headers)
    if h2_res.status_code != 200:
        print("無法讀取頂層內容")
        return
    
    h4_blocks = [b for b in h2_res.json().get("results", []) if b["type"] == "heading_4"]
    print(f"在頂層容器中找到 {len(h4_blocks)} 題")

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
        feedback_block = None
        
        # 使用 Emoji 定位：✏️ 為答案，🤖 為結果
        for cb in children:
            if cb["type"] == "callout":
                text = cb["callout"]["rich_text"][0]["text"]["content"] if cb["callout"]["rich_text"] else ""
                if "✏️" in text:
                    ans_block = cb
                elif "🤖" in text:
                    feedback_block = cb
        
        if ans_block and feedback_block:
            # 精準提取答案字符 (A,B,C,D)
            raw_text = ans_block["callout"]["rich_text"][0]["text"]["content"]
            match = re.search(r"[A-Da-d]", raw_text)
            user_ans = match.group(0).upper() if match else "?"
            
            correct_info = ANSWERS_MAP[questions_processed]
            correct_ans = correct_info["correct"]
            explanation = correct_info["explanation"]
            
            is_correct = (user_ans == correct_ans)
            icon = "✅" if is_correct else "❌"
            result_text = f"{icon} 正確答案：{correct_ans} | 解析：{explanation}"
            
            # PATCH 直接更新 🤖 Block
            patch_url = f"https://api.notion.com/v1/blocks/{feedback_block['id']}"
            patch_payload = {
                "callout": {
                    "rich_text": [{"type": "text", "text": {"content": f"批閱結果：{result_text}"}}]
                }
            }
            patch_res = session.patch(patch_url, json=patch_payload, headers=headers)
            
            if patch_res.status_code == 200:
                print(f"  [OK] 題號 {questions_processed+1}: {user_ans} -> {icon}")
                questions_processed += 1
            else:
                print(f"  [ERROR] 題號 {questions_processed+1}: 寫入失敗")
        else:
            print(f"  [WARN] 題號 {questions_processed+1}: 缺少 ✏️ 或 🤖 block")

    print(f"\\n✨ 批改完成！共處理 {questions_processed} 題。")

if __name__ == "__main__":
    run_grading()
