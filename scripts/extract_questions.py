import json
import os
import re
import hashlib
import tempfile
from datetime import datetime
from pathlib import Path

# Configuration
SESSIONS_DIR = Path.home() / ".pi/agent/sessions/--C--Projects-github-pi-mono--"
INDEX_DIR = Path.home() / ".pi/memory/question_index"
CHECKPOINT_FILE = INDEX_DIR / ".checkpoint.json"
INDEX_DIR.mkdir(parents=True, exist_ok=True)

# Refined Question Detection Patterns
QUESTION_PATTERNS = [
    r"[？?]$", 
    r"^(如何|什麼|為什麼|怎麼|哪些|誰|能否|能不能|有沒有|是否|可以|想知道).*",
    r".*(幫我|請你).*(查|找|看|做|寫|分析|解釋|確認).*",
    r".*(差別|區別)是什麼.*",
]

def is_question(text):
    if not text:
        return False
    if len(text) < 2 and not re.search(r"[？?]", text):
        return False
    return any(re.search(pattern, text) for pattern in QUESTION_PATTERNS)

def get_text_from_content(content_list):
    text = ""
    if not content_list:
        return ""
    for item in content_list:
        if isinstance(item, dict) and item.get("type") == "text":
            text += item.get("text", "")
    return text.strip()

def safe_write_json(path, data):
    """Atomic write using tempfile to prevent corruption."""
    fd, temp_path = tempfile.mkstemp(dir=path.parent, text=True)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(temp_path, path)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e

def extract_questions():
    # Load checkpoint
    checkpoint = {}
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
        except Exception:
            checkpoint = {}

    all_extracted_this_run = []
    processed_files_count = 0
    skipped_files_count = 0
    malformed_lines_count = 0

    if not SESSIONS_DIR.exists():
        print(f"Sessions directory not found: {SESSIONS_DIR}")
        return

    session_files = sorted(SESSIONS_DIR.glob("*.jsonl"))
    
    for session_file in session_files:
        fname = session_file.name
        mtime = session_file.stat().st_mtime
        
        if fname in checkpoint and checkpoint[fname] >= mtime:
            skipped_files_count += 1
            continue

        try:
            session_id = "unknown"
            prev_msg_text = ""
            
            with open(session_file, 'r', encoding='utf-8', errors='replace') as f:
                for line_num, line in enumerate(f):
                    try:
                        data = json.loads(line)
                        
                        # 1. Robust Session ID extraction
                        if session_id == "unknown":
                            if data.get("type") == "session":
                                session_id = data.get("id", "unknown")
                            elif data.get("sessionId"):
                                session_id = data["sessionId"]

                        if data.get("type") == "message":
                            msg_data = data.get("message", {})
                            role = msg_data.get("role")
                            text = get_text_from_content(msg_data.get("content", []))
                            
                            if role == "user" and is_question(text):
                                ts = data.get("timestamp")
                                if not ts: 
                                    continue
                                
                                q_hash = hashlib.sha1(f"{ts}{text}".encode('utf-8')).hexdigest()
                                
                                all_extracted_this_run.append({
                                    "id": q_hash,
                                    "timestamp": ts,
                                    "question": text,
                                    "session_id": session_id,
                                    "file": fname,
                                    "context": {
                                        "before": prev_msg_text[:100],
                                        "after": "" 
                                    }
                                })
                            
                            prev_msg_text = text
                            
                    except json.JSONDecodeError:
                        malformed_lines_count += 1
                        continue
            
            checkpoint[fname] = mtime
            processed_files_count += 1

        except Exception as e:
            print(f"Error processing {fname}: {e}")

    safe_write_json(CHECKPOINT_FILE, checkpoint)

    if not all_extracted_this_run:
        print(f"No new questions found. (Processed: {processed_files_count}, Skipped: {skipped_files_count})")
        return

    all_extracted_this_run.sort(key=lambda x: x['timestamp'])
    
    monthly_buckets = {}
    for q in all_extracted_this_run:
        month = q['timestamp'][:7]
        if month not in monthly_buckets:
            monthly_buckets[month] = []
        monthly_buckets[month].append(q)

    for month, questions in monthly_buckets.items():
        index_file = INDEX_DIR / f"{month}.jsonl"
        existing_hashes = set()
        
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        existing_hashes.add(json.loads(line).get("id"))
                    except: pass
        
        with open(index_file, 'a', encoding='utf-8') as f:
            for q in questions:
                if q['id'] not in existing_hashes:
                    f.write(json.dumps(q, ensure_ascii=False) + "\n")
                    existing_hashes.add(q['id'])

    print(f"Indexing Complete: {processed_files_count} files processed, {len(all_extracted_this_run)} new questions added. (Malformed lines: {malformed_lines_count})")

if __name__ == "__main__":
    extract_questions()
