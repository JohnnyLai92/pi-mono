import json
import os
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Configuration
INDEX_DIR = Path.home() / ".pi/memory/question_index"
REPORT_DIR = Path.home() / ".pi/memory/question_reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

def generate_monthly_report(month):
    """
    Generates a Markdown report from the JSONL index for a specific month.
    """
    index_file = INDEX_DIR / f"{month}.jsonl"
    report_file = REPORT_DIR / f"{month}_report.md"
    
    if not index_file.exists():
        print(f"No index found for month: {month}")
        return

    questions = []
    with open(index_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                questions.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if not questions:
        print(f"No questions to report for {month}")
        return

    # Sort questions by timestamp
    questions.sort(key=lambda x: x['timestamp'])

    # Group by Date for Markdown organization
    daily_groups = defaultdict(list)
    for q in questions:
        # Parse timestamp: 2026-04-29T...
        date_str = q['timestamp'][:10]
        time_str = q['timestamp'][11:16]
        daily_groups[date_str].append((time_str, q))

    # Build Markdown Content
    lines = [
        f"# ❓ 強尼的問題紀錄 ({month})",
        f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        ""
    ]

    for date in sorted(daily_groups.keys()):
        lines.append(f"## 📅 {date}")
        for time_str, q in daily_groups[date]:
            q_text = q['question']
            # Basic Tagging (can be improved with NLP in later stages)
            tags = []
            if "如何" in q_text or "怎麼" in q_text: tags.append("#方法")
            if "什麼" in q_text or "哪些" in q_text: tags.append("#定義")
            if "為什麼" in q_text: tags.append("#原因")
            
            tag_str = " ".join([f"🏷️ {t}" for t in tags])
            
            lines.append(f"- **[{time_str}]** 「{q_text}」")
            if tag_str:
                lines.append(f"  {tag_str}")
            lines.append("") # Spacer

    lines.append("---")
    lines.append("*報告自動生成，僅供回顧使用。*")

    # Write report
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    
    print(f"Report generated: {report_file}")

if __name__ == "__main__":
    # Example usage: run for current month
    current_month = datetime.now().strftime('%Y-%m')
    generate_monthly_report(current_month)
