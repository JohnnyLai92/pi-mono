import os
import re
import requests

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

def run():
    token = os.getenv("NOTION_TOKEN")
    page_id = "34caad32-6752-8127-a846-eed9a69e0de5"
    headers = {"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
    session = requests.Session()
    session.verify = False

    res = session.get(f"https://api.notion.com/v1/blocks/{page_id}/children", headers=headers)
    top_blocks = res.json().get("results", [])
    top_toggle = next((b for b in top_blocks if b["type"] == "heading_2" and b["heading_2"].get("is_toggleable")), None)
    if not top_toggle: return print("找不到頂層 Toggle")

    h2_res = session.get(f"https://api.notion.com/v1/blocks/{top_toggle['id']}/children", headers=headers)
    h4_blocks = [b for b in h2_res.json().get("results", []) if b["type"] == "heading_4"]
    
    for i, h4 in enumerate(h4_blocks):
        if i >= len(ANSWERS_MAP): break
        h4_id = h4["id"]
        child_res = session.get(f"https://api.notion.com/v1/blocks/{h4_id}/children", headers=headers)
        children = child_res.json().get("results", [])
        
        ans_block = None
        feedback_block = None
        for cb in children:
            if cb["type"] == "callout":
                text = cb["callout"]["rich_text"][0]["text"]["content"] if cb["callout"]["rich_text"] else ""
                if "✏️" in text: ans_block = cb
                elif "🤖" in text: feedback_block = cb
        
        if ans_block and feedback_block:
            text_content = ans_block["callout"]["rich_text"][0]["text"]["content"]
            match = re.search(r"[A-Da-d]", text_content)
            user_ans = match.group(0).upper() if match else "?"
            correct_ans = ANSWERS_MAP[i]["correct"]
            explanation = ANSWERS_MAP[i]["explanation"]
            icon = "✅" if user_ans == correct_ans else "❌"
            res_text = f"批閱結果：{icon} 正確答案：{correct_ans} | 解析：{explanation}"
            session.patch(f"https://api.notion.com/v1/blocks/{feedback_block['id']}", json={"callout": {"rich_text": [{"type": "text", "text": {"content": res_text}}]}}, headers=headers)
            print(f"題 {i+1}: {user_ans} -> {icon}")

if __name__ == "__main__":
    run()
