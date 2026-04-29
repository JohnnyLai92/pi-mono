#!/usr/bin/env python3
"""
AI 應用規劃師題型練習 - 排程管理器

功能：
1. 每日早上 8:00 自動生成新試卷（單數日基礎版，雙數日進階版）
2. 每小時自動巡檢並批改試卷
3. 批改完成後發送 Email 通知

使用方式：
    # 手動執行
    python ai_quiz_scheduler.py --action=generate
    python ai_quiz_scheduler.py --action=grade
    python ai_quiz_scheduler.py --action=check
    
    # 加入 crontab（Linux/Mac）
    0 8 * * * cd /path/to/pi-mono && python packages/mom/src/skills/ai_quiz_scheduler.py --action=generate
    0 * * * * cd /path/to/pi-mono && python packages/mom/src/skills/ai_quiz_scheduler.py --action=grade
    
    # 加入 Windows 排程工作
    參見 docs/windows_task_scheduler.md
"""

import os
import sys
import argparse
import json
from datetime import datetime
from pathlib import Path

# 載入環境變數
from dotenv import load_dotenv
load_dotenv()

# 加入上層目錄到路徑
sys.path.insert(0, str(Path(__file__).parent))

from ai_quiz_manager import AIQuizManager, generate_ai_quiz, grade_ai_quizzes


def send_email_notification(grading_result: dict):
    """
    發送批改結果 Email 通知
    
    使用既有的 Email Skill 發送
    """
    try:
        # 嘗試導入 Email Skill
        from email_utils import send_email  # 假設存在此模組
        
        subject = f"[小白報報] AI 應用規劃師模擬試卷批改完成 - {datetime.now().strftime('%Y-%m-%d')}"
        
        # 建立 HTML 內容
        html_content = f"""
        <html>
        <body>
            <h2>📊 AI 應用規劃師模擬試卷批改報告</h2>
            <p>批改時間：{grading_result['checked_at']}</p>
            
            <h3>📈 批改統計</h3>
            <ul>
                <li>發現試卷：{grading_result['quizzes_found']} 份</li>
                <li>完成批改：{len(grading_result['quizzes_graded'])} 份</li>
            </ul>
            
            <h3>📝 詳細成績</h3>
            <table border="1" cellpadding="5" style="border-collapse: collapse;">
                <tr style="background-color: #f0f0f0;">
                    <th>試卷名稱</th>
                    <th>正確題數</th>
                    <th>總題數</th>
                    <th>分數</th>
                </tr>
        """
        
        for quiz in grading_result['quizzes_graded']:
            score_color = "#28a745" if quiz['score'] >= 80 else "#ffc107" if quiz['score'] >= 60 else "#dc3545"
            html_content += f"""
                <tr>
                    <td>{quiz['heading_text']}</td>
                    <td>{quiz['correct']}</td>
                    <td>{quiz['total']}</td>
                    <td style="color: {score_color}; font-weight: bold;">{quiz['score']}分</td>
                </tr>
            """
        
        html_content += """
            </table>
            
            <h3>💡 後續建議</h3>
            <ul>
                <li>查看 Notion 頁面獲取詳細解析</li>
                <li>針對錯題加強複習</li>
                <li>明日將自動生成新試卷</li>
            </ul>
            
            <p style="margin-top: 30px;">
                <em>-- 小白 自動發送 🐶</em>
            </p>
        </body>
        </html>
        """
        
        # 發送 Email（需設定收件人）
        recipient = os.getenv('JOHNNY_EMAIL', 'johnny@example.com')
        send_email(
            to=recipient,
            subject=subject,
            html=html_content
        )
        
        print(f"✅ Email 通知已發送至 {recipient}")
        
    except ImportError:
        print("⚠️  Email Skill 未導入，跳過通知發送")
    except Exception as e:
        print(f"⚠️  Email 發送失敗：{e}")


def daily_generate():
    """
    每日自動生成試卷
    
    規則：
    - 單數日：基礎版（NLP 主題）
    - 雙數日：進階版（跨領域主題）
    """
    today = datetime.now()
    day = today.day
    difficulty = 'basic' if day % 2 == 1 else 'advanced'
    difficulty_name = '基礎版' if difficulty == 'basic' else '進階版'
    
    print(f"\n{'='*60}")
    print(f"📅 每日自動生成試卷 - {today.strftime('%Y-%m-%d')}")
    print(f"   今日日期：{day}日（{'單數' if day % 2 == 1 else '雙數'}）")
    print(f"   生成難度：{difficulty_name}")
    print(f"{'='*60}\n")
    
    result = generate_ai_quiz(difficulty)
    
    if result.get('success'):
        print(f"\n✅ 試卷生成成功！")
        print(f"   題數：{result.get('question_count')}")
        print(f"   時間：{result.get('timestamp')}")
    else:
        print(f"\n❌ 試卷生成失敗：{result.get('error')}")
    
    return result


def hourly_grade():
    """
    每小時自動巡檢並批改試卷
    """
    now = datetime.now()
    
    print(f"\n{'='*60}")
    print(f"⏰ 每小時自動批改 - {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    result = grade_ai_quizzes()
    
    # 如果有批改結果，發送 Email 通知
    if result['quizzes_graded']:
        print(f"\n📧 發送 Email 通知...")
        send_email_notification(result)
    else:
        print(f"\nℹ️  無需批改的試卷")
    
    return result


def manual_check():
    """
    手動檢查待批改試卷（不執行批改）
    """
    manager = AIQuizManager()
    pending = manager.check_pending_grading()
    
    print(f"\n{'='*60}")
    print(f"🔍 待批改試卷檢查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    if not pending:
        print("✅ 目前沒有待批改的試卷")
    else:
        print(f"📝 找到 {len(pending)} 份待批改試卷：\n")
        
        for i, quiz in enumerate(pending, 1):
            print(f"{i}. {quiz['heading_text']}")
            print(f"   待批改題數：{len(quiz['questions'])}")
            print(f"   題目預覽：")
            for j, q in enumerate(quiz['questions'][:3], 1):  # 只顯示前 3 題
                print(f"     {j}. {q['question'][:50]}... (答案：{q['user_answer']})")
            if len(quiz['questions']) > 3:
                print(f"     ... 還有 {len(quiz['questions']) - 3} 題")
            print()
    
    return pending


def main():
    parser = argparse.ArgumentParser(
        description='AI 應用規劃師題型練習排程管理器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例：
  # 生成新試卷
  python ai_quiz_scheduler.py --action=generate
  
  # 批改試卷
  python ai_quiz_scheduler.py --action=grade
  
  # 檢查待批改試卷（不批改）
  python ai_quiz_scheduler.py --action=check
  
  # 完整測試（生成 + 檢查 + 批改）
  python ai_quiz_scheduler.py --action=all
        """
    )
    
    parser.add_argument(
        '--action',
        type=str,
        choices=['generate', 'grade', 'check', 'all'],
        default='check',
        help='執行動作：generate(生成試卷), grade(批改試卷), check(檢查), all(全部)'
    )
    
    parser.add_argument(
        '--difficulty',
        type=str,
        choices=['basic', 'advanced'],
        default=None,
        help='指定試卷難度（僅在 generate 動作時有效，預設依日期自動判斷）'
    )
    
    parser.add_argument(
        '--send-email',
        action='store_true',
        help='批改完成後發送 Email 通知'
    )
    
    args = parser.parse_args()
    
    if args.action == 'generate':
        difficulty = args.difficulty
        if not difficulty:
            # 自動判斷
            day = datetime.now().day
            difficulty = 'basic' if day % 2 == 1 else 'advanced'
        return daily_generate()
    
    elif args.action == 'grade':
        result = hourly_grade()
        if args.send_email and result['quizzes_graded']:
            send_email_notification(result)
        return result
    
    elif args.action == 'check':
        return manual_check()
    
    elif args.action == 'all':
        print("🔄 執行完整測試流程...\n")
        
        # 1. 生成試卷
        gen_result = daily_generate()
        print("\n等待 3 秒讓 Notion 同步...\n")
        time.sleep(3)
        
        # 2. 檢查
        check_result = manual_check()
        print("\n" + "="*60 + "\n")
        
        # 3. 批改
        grade_result = hourly_grade()
        
        return {
            'generate': gen_result,
            'check': check_result,
            'grade': grade_result
        }


if __name__ == "__main__":
    import time  # 用於 all 動作的延遲
    main()
