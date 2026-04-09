#!/usr/bin/env python3
"""
xiaobao.py — 小寶 Agent Client
================================
大寶透過此腳本與小寶（本地 Gemma 4 31B）溝通。
使用 ACTION/PARAMS 文字格式進行工具呼叫。

使用方式：
  python3 harness/xiaobao.py --task "寫一個 Python 腳本" --workdir .
  echo "修改 app.py" | python3 harness/xiaobao.py --stdin
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# 設定
# ──────────────────────────────────────────────────────────────────────────────

DEFAULT_BASE_URL = "http://localhost:8080/v1"
DEFAULT_MODEL = "dealignai/Gemma-4-31B-JANG_4M-CRACK"
MAX_TURNS = 20
MAX_TOKENS = 4096
TIMEOUT = 120

GIT_BLOCKED = ["git add", "git commit", "git push", "git reset --hard",
               "git clean -fd", "git push --force"]

# ──────────────────────────────────────────────────────────────────────────────
# 系統提示詞
# ──────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """你是「小寶」，大寶的程式開發助手。一律使用繁體中文。
禁止 git add/commit/push。檔案操作僅限工作目錄 {workdir}。

你透過 ACTION 指令操作系統。每次回覆只能發出一個 ACTION。

## 可用 ACTION

ACTION: bash
COMMAND: <bash 指令>

ACTION: read
PATH: <檔案路徑>

ACTION: write
PATH: <檔案路徑>
CONTENT:
<檔案內容，直到 END_CONTENT>
END_CONTENT

ACTION: edit
PATH: <檔案路徑>
OLD_TEXT:
<要替換的文字，直到 END_OLD>
END_OLD
NEW_TEXT:
<新文字，直到 END_NEW>
END_NEW

ACTION: done
REPORT: <完成報告>

## 範例

使用者：列出目前目錄的檔案
助手：我來列出目錄檔案。

ACTION: bash
COMMAND: ls -lh

使用者：結果為 total 8 ...
助手：任務完成。

ACTION: done
REPORT: 已列出目錄檔案，共 8 個項目。

## 重要
- 每次回覆必須包含一個 ACTION
- 不要假裝執行指令，必須用 ACTION 讓系統執行
- ACTION: done 表示任務完成"""

# ──────────────────────────────────────────────────────────────────────────────
# 工具實作
# ──────────────────────────────────────────────────────────────────────────────

def validate_path(path_str: str, workdir: str) -> str:
    abs_path = os.path.abspath(os.path.join(workdir, path_str))
    abs_workdir = os.path.abspath(workdir)
    if not abs_path.startswith(abs_workdir):
        raise PermissionError(f"⛔ 路徑超出工作目錄：{abs_path}")
    return abs_path


def exec_bash(command: str, workdir: str) -> str:
    if not command.strip():
        return "❌ 指令為空"
    for blocked in GIT_BLOCKED:
        if blocked in command.lower():
            return f"⛔ 禁止 Git 操作：{blocked}"
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True,
                           timeout=60, cwd=workdir)
        out = (r.stdout or "") + (("\n--- stderr ---\n" + r.stderr) if r.stderr else "")
        if not out.strip():
            out = f"(exit code: {r.returncode})"
        if len(out) > 8000:
            out = out[:4000] + "\n...(截斷)...\n" + out[-2000:]
        return out
    except subprocess.TimeoutExpired:
        return "❌ 逾時（60s）"
    except Exception as e:
        return f"❌ {e}"


def exec_read(path_str: str, workdir: str) -> str:
    try:
        abs_path = validate_path(path_str, workdir)
        if not os.path.exists(abs_path):
            return f"❌ 不存在：{path_str}"
        content = Path(abs_path).read_text(encoding="utf-8", errors="replace")
        if len(content) > 10000:
            content = content[:5000] + "\n...(截斷)...\n" + content[-2000:]
        return content
    except Exception as e:
        return f"❌ {e}"


def exec_write(path_str: str, content: str, workdir: str) -> str:
    try:
        abs_path = validate_path(path_str, workdir)
        Path(abs_path).parent.mkdir(parents=True, exist_ok=True)
        Path(abs_path).write_text(content, encoding="utf-8")
        return f"✅ 已寫入 {path_str} ({len(content):,} chars)"
    except Exception as e:
        return f"❌ {e}"


def exec_edit(path_str: str, old_text: str, new_text: str, workdir: str) -> str:
    try:
        abs_path = validate_path(path_str, workdir)
        if not os.path.exists(abs_path):
            return f"❌ 不存在：{path_str}"
        content = Path(abs_path).read_text(encoding="utf-8")
        if old_text not in content:
            return "❌ 找不到 old_text"
        if content.count(old_text) > 1:
            return f"⚠️ old_text 出現 {content.count(old_text)} 次"
        Path(abs_path).write_text(content.replace(old_text, new_text, 1), encoding="utf-8")
        return f"✅ 已替換 {path_str}"
    except Exception as e:
        return f"❌ {e}"


# ──────────────────────────────────────────────────────────────────────────────
# 解析 ACTION
# ──────────────────────────────────────────────────────────────────────────────

def parse_action(text: str) -> dict | None:
    """從回覆中解析 ACTION 指令"""
    # ACTION: done
    m = re.search(r'ACTION:\s*done\s*\nREPORT:\s*(.*)', text, re.DOTALL | re.IGNORECASE)
    if m:
        return {"action": "done", "report": m.group(1).strip()}

    # ACTION: bash
    m = re.search(r'ACTION:\s*bash\s*\nCOMMAND:\s*(.+)', text, re.IGNORECASE)
    if m:
        return {"action": "bash", "command": m.group(1).strip()}

    # ACTION: read
    m = re.search(r'ACTION:\s*read\s*\nPATH:\s*(.+)', text, re.IGNORECASE)
    if m:
        return {"action": "read", "path": m.group(1).strip()}

    # ACTION: write
    m = re.search(r'ACTION:\s*write\s*\nPATH:\s*(.+?)\s*\nCONTENT:\s*\n(.*?)\nEND_CONTENT', text, re.DOTALL | re.IGNORECASE)
    if m:
        return {"action": "write", "path": m.group(1).strip(), "content": m.group(2)}

    # ACTION: edit
    m = re.search(r'ACTION:\s*edit\s*\nPATH:\s*(.+?)\s*\nOLD_TEXT:\s*\n(.*?)\nEND_OLD\s*\nNEW_TEXT:\s*\n(.*?)\nEND_NEW', text, re.DOTALL | re.IGNORECASE)
    if m:
        return {"action": "edit", "path": m.group(1).strip(),
                "old_text": m.group(2), "new_text": m.group(3)}

    return None


# ──────────────────────────────────────────────────────────────────────────────
# LLM API
# ──────────────────────────────────────────────────────────────────────────────

def call_llm(messages: list[dict], base_url: str, model: str) -> str:
    import urllib.request
    payload = json.dumps({
        "model": model, "messages": messages,
        "max_tokens": MAX_TOKENS, "temperature": 0.3,
    }).encode()
    req = urllib.request.Request(f"{base_url}/chat/completions", data=payload,
                                headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read())["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ LLM 錯誤：{e}"


# ──────────────────────────────────────────────────────────────────────────────
# Agent 主迴圈
# ──────────────────────────────────────────────────────────────────────────────

def run_agent(task: str, workdir: str, base_url: str = DEFAULT_BASE_URL,
              model: str = DEFAULT_MODEL, verbose: bool = True) -> str:
    workdir = os.path.abspath(workdir)
    if verbose:
        print(f"{'='*60}")
        print(f"🤖 小寶 Agent 啟動")
        print(f"  任務：{task[:80]}{'...' if len(task) > 80 else ''}")
        print(f"  工作目錄：{workdir}")
        print(f"{'='*60}")

    system = SYSTEM_PROMPT.format(workdir=workdir)
    messages: list[dict] = [
        {"role": "system", "content": system},
        # few-shot 範例
        {"role": "user", "content": "大寶指派任務：確認工作目錄"},
        {"role": "assistant", "content": "我來確認工作目錄。\n\nACTION: bash\nCOMMAND: pwd"},
        {"role": "user", "content": f"執行結果：\n{workdir}"},
        {"role": "assistant", "content": f"ACTION: done\nREPORT: 工作目錄為 {workdir}"},
        # 實際任務
        {"role": "user", "content": f"大寶指派任務：\n\n{task}"},
    ]

    for turn in range(1, MAX_TURNS + 1):
        if verbose:
            print(f"\n--- Turn {turn}/{MAX_TURNS} ---")

        response = call_llm(messages, base_url, model)

        if response.startswith("❌"):
            if verbose:
                print(f"⚠️ {response}")
            return response

        # 解析 ACTION
        action = parse_action(response)

        if action is None:
            # 沒有 ACTION，可能是最終回答
            if verbose:
                display = response[:300] + "..." if len(response) > 300 else response
                print(f"💬 {display}")
            # 再問一次要不要發 done
            messages.append({"role": "assistant", "content": response})
            messages.append({"role": "user", "content": "請用 ACTION: done 發出完成報告，或用其他 ACTION 繼續執行。"})
            continue

        if action["action"] == "done":
            report = action.get("report", "任務完成")
            if verbose:
                print(f"📝 {report}")
                print(f"\n✅ 小寶完成（共 {turn} 輪）")
            return f"## 小寶完成報告\n{report}"

        # 執行工具
        if action["action"] == "bash":
            cmd = action["command"]
            if verbose:
                print(f"🔧 bash: {cmd[:80]}")
            result = exec_bash(cmd, workdir)

        elif action["action"] == "read":
            p = action["path"]
            if verbose:
                print(f"🔧 read: {p}")
            result = exec_read(p, workdir)

        elif action["action"] == "write":
            p = action["path"]
            if verbose:
                print(f"🔧 write: {p}")
            result = exec_write(p, action["content"], workdir)

        elif action["action"] == "edit":
            p = action["path"]
            if verbose:
                print(f"🔧 edit: {p}")
            result = exec_edit(p, action["old_text"], action["new_text"], workdir)
        else:
            result = f"❌ 未知 ACTION：{action['action']}"

        if verbose:
            display = result[:300] + "..." if len(result) > 300 else result
            print(f"📋 {display}")

        messages.append({"role": "assistant", "content": response})
        messages.append({"role": "user", "content": f"執行結果：\n{result}"})

    return f"⚠️ 超過 {MAX_TURNS} 輪，強制停止。"


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="小寶 Agent — 大寶的技術執行助手")
    parser.add_argument("--task", type=str, help="任務描述")
    parser.add_argument("--stdin", action="store_true")
    parser.add_argument("--workdir", type=str, default=os.getcwd())
    parser.add_argument("--base-url", type=str, default=DEFAULT_BASE_URL)
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    task = sys.stdin.read().strip() if args.stdin else (args.task or "")
    if not task:
        parser.print_help()
        sys.exit(1)

    try:
        import urllib.request
        with urllib.request.urlopen(f"{args.base_url}/models", timeout=5):
            pass
    except Exception:
        print(f"❌ 無法連線 LLM：{args.base_url}", file=sys.stderr)
        sys.exit(1)

    result = run_agent(task=task, workdir=args.workdir, base_url=args.base_url,
                       model=args.model, verbose=not args.quiet)
    if args.quiet:
        print(result)


if __name__ == "__main__":
    main()
