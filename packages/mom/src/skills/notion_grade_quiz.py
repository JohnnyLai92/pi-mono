import os
import re
import sys
import requests
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Optional

# Fix 1: UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def extract_text(block: dict) -> str:
    """Extract plain text from a Notion block (any type)."""
    b_type = block.get("type", "")
    rich_text = block.get(b_type, {}).get("rich_text", [])
    return "".join(t.get("plain_text", "") for t in rich_text)


# Fix 3: Regex extraction — tolerates (C), C., 答案C, extra spaces
def extract_answer(text: str) -> str:
    match = re.search(r"[A-Da-d]", text)
    return match.group(0).upper() if match else ""

def get_page_blocks(token, page_id):
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers, verify=False)
    return response.json().get("results", [])

# Fix 2: DFS recursive child fetch (discovers answers in nested blocks)
def get_block_children_recursive(token: str, block_id: str, depth: int = 0, max_depth: int = 3) -> list:
    if depth > max_depth:
        return []
    url = f"https://api.notion.com/v1/blocks/{block_id}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code != 200:
        print(f"  [warn] GET children {block_id} → {response.status_code}")
        return []
    blocks = response.json().get("results", [])
    for b in blocks:
        if b.get("has_children"):
            b["_children"] = get_block_children_recursive(token, b["id"], depth + 1, max_depth)
    return blocks


def find_callout_by_emoji(blocks: list, emoji: str) -> Optional[dict]:
    """Recursively search for a callout with a matching icon emoji."""
    for b in blocks:
        if b.get("type") == "callout":
            icon = b.get("callout", {}).get("icon", {})
            if icon.get("emoji") == emoji:
                return b
        found = find_callout_by_emoji(b.get("_children", []), emoji)
        if found:
            return found
    return None


# Fix 5: Correct callout payload (already correct here, kept and confirmed)
def update_block_content(token: str, block_id: str, text: str) -> None:
    url = f"https://api.notion.com/v1/blocks/{block_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }
    payload = {
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }
    response = requests.patch(url, json=payload, headers=headers, verify=False)
    if response.status_code != 200:
        print(f"  [warn] PATCH {block_id} → {response.status_code}: {response.text[:120]}")


# Fix 6: LLM-generated explanation via `claude -p`
def generate_explanation(question_text: str, correct: str, user: str) -> str:
    import subprocess
    verdict = "答對" if user.upper() == correct.upper() else "答錯"
    prompt = (
        f"以下是一道 AI / NLP 選擇題：\n{question_text}\n\n"
        f"正確答案是 ({correct})。使用者選了 ({user or '未作答'})，{verdict}。\n"
        "請用 2–3 句繁體中文說明為何此答案正確，以及其他選項錯在哪裡。"
        "不要加任何標題或格式，直接輸出說明文字。"
    )
    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True, text=True, encoding="utf-8", timeout=60,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception as e:
        print(f"  [warn] LLM call failed: {e}")
    return f"正確答案為 ({correct})。"


def grade_quiz(token: str, page_id: str, answer_key: dict, max_workers: int = 8) -> list:
    """Grade quiz using ThreadPoolExecutor to parallelize Notion + LLM calls.

    Fix 4 (sync version): N+1 serial requests → 3 concurrent batches.
    Notion API rate limit is ~3 req/s; max_workers=8 stays well under.
    """
    blocks = get_page_blocks(token, page_id)

    questions = [
        b for b in blocks
        if b.get("type") == "heading_2" and b["heading_2"].get("is_toggleable")
    ]
    if not questions:
        questions = [b for b in blocks if b.get("type") == "heading_4"]

    if not questions:
        print("No question blocks found.")
        return []

    # Stage 1: parallel DFS fetch for all question children
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        children_lists = list(pool.map(
            lambda q: get_block_children_recursive(token, q["id"]),
            questions,
        ))

    # Stage 2: parse (no I/O)
    parsed = []
    for i, (q_block, children) in enumerate(zip(questions, children_lists), 1):
        q_text = extract_text(q_block)
        answer_block = find_callout_by_emoji(children, "✏️")
        feedback_block = find_callout_by_emoji(children, "🤖")

        raw = extract_text(answer_block) if answer_block else ""
        raw = re.sub(r"我的答案[:：]\s*", "", raw)
        user_answer = extract_answer(raw)

        correct_ans = answer_key.get(i, "N/A")
        is_correct = user_answer.upper() == correct_ans.upper() if user_answer else False

        parsed.append({
            "i": i, "q_text": q_text, "user_answer": user_answer,
            "correct": correct_ans, "is_correct": is_correct,
            "feedback_block": feedback_block,
        })

    # Stage 3: parallel LLM explanations
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        explanations = list(pool.map(
            lambda p: generate_explanation(p["q_text"], p["correct"], p["user_answer"]),
            parsed,
        ))

    # Stage 4: parallel PATCH updates
    update_args = []
    results = []
    for p, explanation in zip(parsed, explanations):
        verdict = "✅ 正確" if p["is_correct"] else "❌ 錯誤"
        feedback = (
            f"【{verdict}】\n"
            f"正確答案：({p['correct']})\n"
            f"【解析】：{explanation}"
        )
        if p["feedback_block"]:
            update_args.append((p["feedback_block"]["id"], feedback))

        results.append({
            "q": p["i"],
            "question": p["q_text"][:30] + ("..." if len(p["q_text"]) > 30 else ""),
            "user": p["user_answer"] or "(未作答)",
            "correct": p["correct"],
            "result": "Correct" if p["is_correct"] else "Wrong",
        })

    if update_args:
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            list(pool.map(
                lambda args: update_block_content(token, args[0], args[1]),
                update_args,
            ))

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
