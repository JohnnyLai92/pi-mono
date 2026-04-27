import os
import requests
from typing import List, Dict, Any

def extract_text(block):
    """Extract plain text from a Notion block."""
    b_type = block.get("type")
    if b_type not in ["callout", "paragraph", "heading_1", "heading_2", "heading_3"]:
        return ""
    
    rich_text = block[b_type].get("rich_text", [])
    return "".join([t.get("plain_text", "") for t in rich_text])

def get_page_blocks(token, page_id):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers, verify=False)
    return response.json().get("results", [])

def get_block_children(token, block_id):
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers, verify=False)
    return response.json().get("results", [])

def update_block_content(token, block_id, text):
    url = f"https://api.notion.com/v1/blocks/{block_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    payload = {
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }
    requests.patch(url, json=payload, headers=headers, verify=False)

def grade_quiz(token, page_id, answer_key):
    blocks = get_page_blocks(token, page_id)
    
    # Find all Toggle H2s
    questions = [b for b in blocks if b.get("type") == "heading_2" and b["heading_2"].get("is_toggleable")]
    
    results = []
    
    for i, q_block in enumerate(questions):
        q_id = q_block["id"]
        q_text = extract_text(q_block)
        
        children = get_block_children(token, q_id)
        
        answer_block = None
        feedback_block = None
        
        for child in children:
            if child.get("type") == "callout":
                emoji = child["callout"].get("icon", {}).get("emoji", "")
                if emoji == "✏️":
                    answer_block = child
                elif emoji == "🤖":
                    feedback_block = child
        
        user_answer = ""
        if answer_block:
            user_answer = extract_text(answer_block).replace("我的答案：", "").strip()
        
        correct_ans = answer_key.get(i + 1, "N/A")
        is_correct = user_answer.upper() == correct_ans.upper()
        
        # Construct feedback
        feedback = f"【{'✅ 正確' if is_correct else '❌ 錯誤'}】\n正確答案：{correct_ans}"
        
        # Update Notion
        if feedback_block:
            update_block_content(token, feedback_block["id"], feedback)
            
        results.append({
            "q": q_text[:20] + "...",
            "user": user_answer,
            "correct": correct_ans,
            "result": "Correct" if is_correct else "Wrong"
        })
        
    return results

if __name__ == "__main__":
    token = os.getenv("NOTION_TOKEN")
    page_id = "34caad32-6752-8127-a846-eed9a69e0de5"
    answer_key = {
        1: "C",
        2: "B",
        3: "C",
        4: "B",
        5: "C"
    }
    
    res = grade_quiz(token, page_id, answer_key)
    for r in res:
        print(r)
