"""
grade_ai_exam.py — Notion quiz auto-grader

Fixes applied:
  1. UTF-8 stdout reconfiguration (UnicodeEncodeError prevention)
  2. Recursive block fetching (DFS, not shallow single-level read)
  3. Regex-based answer extraction (tolerates "(C)", "答案 C", extra spaces)
  4. Async concurrent API requests via aiohttp (eliminates N+1 serial calls)
  5. Correct Notion patch payload: {"callout": {"rich_text": [...]}}
  6. LLM-generated explanations via `claude -p` CLI
"""

import asyncio
import os
import re
import subprocess
import sys
from typing import Optional

import aiohttp
from dotenv import load_dotenv

# Fix 1: UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

load_dotenv()

TOKEN = os.getenv("NOTION_TOKEN")
PAGE_ID = "34caad3267528127a846eed9a69e0de5"
NOTION_VERSION = "2022-06-28"
BASE_URL = "https://api.notion.com/v1"

ANSWER_KEY = {
    1: "C",
    2: "B",
    3: "C",
    4: "B",
    5: "C",
    6: "B",
    7: "B",
    8: "B",
    9: "B",
    10: "B",
}


def notion_headers() -> dict:
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def extract_plain_text(block: dict) -> str:
    b_type = block.get("type", "")
    rich_text = block.get(b_type, {}).get("rich_text", [])
    return "".join(t.get("plain_text", "") for t in rich_text)


# Fix 3: Regex extraction — tolerates (C), C., 答案C, extra spaces
def extract_answer(text: str) -> str:
    match = re.search(r"[A-Da-d]", text)
    return match.group(0).upper() if match else ""


# Fix 2: DFS recursive block fetch (discovers answers in nested children)
async def fetch_blocks_recursive(
    session: aiohttp.ClientSession,
    block_id: str,
    depth: int = 0,
    max_depth: int = 3,
) -> list[dict]:
    if depth > max_depth:
        return []
    url = f"{BASE_URL}/blocks/{block_id}/children"
    async with session.get(url, headers=notion_headers(), ssl=False) as resp:
        if resp.status != 200:
            print(f"  [warn] GET {url} → {resp.status}")
            return []
        data = await resp.json()
    blocks = data.get("results", [])
    # Fetch children for blocks that have_children concurrently
    child_tasks = [
        fetch_blocks_recursive(session, b["id"], depth + 1, max_depth)
        for b in blocks
        if b.get("has_children")
    ]
    child_results = await asyncio.gather(*child_tasks)
    # Attach fetched children back onto parent blocks
    idx = 0
    for b in blocks:
        if b.get("has_children"):
            b["_children"] = child_results[idx]
            idx += 1
    return blocks


# Fix 5: Correct callout payload structure
async def update_callout(
    session: aiohttp.ClientSession, block_id: str, text: str
) -> None:
    url = f"{BASE_URL}/blocks/{block_id}"
    payload = {
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }
    async with session.patch(
        url, headers=notion_headers(), json=payload, ssl=False
    ) as resp:
        if resp.status != 200:
            body = await resp.text()
            print(f"  [warn] PATCH {block_id} → {resp.status}: {body[:120]}")


def find_callout_by_emoji(blocks: list[dict], emoji: str) -> Optional[dict]:
    """Search recursively for a callout block with a matching icon emoji."""
    for b in blocks:
        if b.get("type") == "callout":
            icon = b.get("callout", {}).get("icon", {})
            if icon.get("emoji") == emoji:
                return b
        found = find_callout_by_emoji(b.get("_children", []), emoji)
        if found:
            return found
    return None


# Fix 6: LLM-generated explanation via `claude -p`
def generate_explanation(question_text: str, correct: str, user: str) -> str:
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
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception as e:
        print(f"  [warn] LLM call failed: {e}")
    return f"正確答案為 ({correct})。"


async def grade_all(questions: list[dict], session: aiohttp.ClientSession) -> list[dict]:
    """Grade all questions concurrently: fetch children, run LLM, batch-update."""

    # Fix 4: Fetch all children concurrently (single gather replaces N serial GETs)
    children_lists = await asyncio.gather(
        *[fetch_blocks_recursive(session, q["id"]) for q in questions]
    )

    # Stage 1: parse all questions (no I/O, fast)
    parsed = []
    for i, (q_block, children) in enumerate(zip(questions, children_lists), 1):
        q_text = extract_plain_text(q_block)
        answer_block = find_callout_by_emoji(children, "✏️")
        feedback_block = find_callout_by_emoji(children, "🤖")

        raw = extract_plain_text(answer_block) if answer_block else ""
        raw = re.sub(r"我的答案[:：]\s*", "", raw)
        user_answer = extract_answer(raw)

        correct = ANSWER_KEY.get(i, "?")
        is_correct = user_answer.upper() == correct.upper() if user_answer else False

        parsed.append({
            "i": i,
            "q_text": q_text,
            "user_answer": user_answer,
            "correct": correct,
            "is_correct": is_correct,
            "feedback_block": feedback_block,
        })

    # Stage 2: Fix 6 — run all LLM explanations concurrently via to_thread
    # Each subprocess.run runs in a worker thread; event loop stays free.
    explanations = await asyncio.gather(
        *[
            asyncio.to_thread(
                generate_explanation, p["q_text"], p["correct"], p["user_answer"]
            )
            for p in parsed
        ]
    )

    # Stage 3: build feedback texts and PATCH concurrently
    results = []
    update_tasks = []
    for p, explanation in zip(parsed, explanations):
        verdict = "✅ 正確" if p["is_correct"] else "❌ 錯誤"
        feedback_text = (
            f"【{verdict}】\n"
            f"正確答案：({p['correct']})\n"
            f"【解析】：{explanation}"
        )

        if p["feedback_block"]:
            update_tasks.append(
                update_callout(session, p["feedback_block"]["id"], feedback_text)
            )

        results.append({
            "q": p["i"],
            "question": p["q_text"][:30] + ("..." if len(p["q_text"]) > 30 else ""),
            "user": p["user_answer"] or "(未作答)",
            "correct": p["correct"],
            "result": "O" if p["is_correct"] else "X",
        })

    # Fix 4: All PATCH requests in a single concurrent gather
    if update_tasks:
        await asyncio.gather(*update_tasks)

    return results


async def main() -> None:
    if not TOKEN:
        print("Error: NOTION_TOKEN not set.")
        sys.exit(1)

    async with aiohttp.ClientSession() as session:
        # Initial page fetch
        url = f"{BASE_URL}/blocks/{PAGE_ID}/children"
        async with session.get(url, headers=notion_headers(), ssl=False) as resp:
            if resp.status != 200:
                print(f"Failed to fetch page: {resp.status}")
                sys.exit(1)
            page_data = await resp.json()

        blocks = page_data.get("results", [])

        # Fix 2: Support both heading_2 (toggleable) and heading_4 structures
        questions = [
            b for b in blocks
            if b.get("type") == "heading_2" and b["heading_2"].get("is_toggleable")
        ]
        if not questions:
            questions = [b for b in blocks if b.get("type") == "heading_4"]

        if not questions:
            print("No question blocks found. Check page structure.")
            sys.exit(1)

        print(f"Found {len(questions)} questions. Grading...")
        results = await grade_all(questions, session)

    print("\n--- Results ---")
    correct_count = sum(1 for r in results if r["result"] == "O")
    for r in results:
        print(f"Q{r['q']:>2} [{r['result']}] user={r['user']} correct={r['correct']}  {r['question']}")
    print(f"\nScore: {correct_count}/{len(results)}")


if __name__ == "__main__":
    asyncio.run(main())
