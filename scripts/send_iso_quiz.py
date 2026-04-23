import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add scripts directory to sys.path to import send_email
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from send_email import send_email

def main():
    subject = "[ISO 27001:2022] LAC 主導稽核員模擬測驗 - 今日挑戰"
    
    questions = [
        "1. 根據 ISO 27001:2022，組織在定義資訊安全管理系統 (ISMS) 的範圍時，應考慮哪些因素？\n   (A) 內部與外部議題\n   (B) 利害關係人的要求\n   (C) 組織的界面與互動\n   (D) 以上皆是",
        "2. 在 ISO 27001 的 Clause 6.1.2 中，風險評估流程必須確保？\n   (A) 能夠產生一致且可重複的結果\n   (B) 僅由資訊安全經理執行\n   (C) 每年僅進行一次\n   (D) 排除所有第三方風險",
        "3. 附錄 A (Annex A) 中的控制措施主要分為哪四大類？\n   (A) 組織、人員、實體、技術\n   (B) 管理、技術、法律、行政\n   (C) 預防、偵測、修正、恢復\n   (D) 內部、外部、供應商、客戶",
        "4. 根據 ISO 19011，在稽核開會 (Opening Meeting) 時，稽核員應該告知什麼？\n   (A) 最終的稽核結果\n   (B) 稽核的目的、範圍與準則\n   (C) 所有的不符合事項 (Non-conformity)\n   (D) 稽核對象的績效評估",
        "5. 在進行資訊安全風險處理 (Risk Treatment) 時，下列哪項不是合法的選擇？\n   (A) 規避 (Avoid)\n   (B) 轉移 (Transfer)\n   (C) 忽略 (Ignore)\n   (D) 降低 (Mitigate)",
        "6. ISO 27001:2022 的 Clause 9.2 要求組織必須進行什麼？\n   (A) 內部稽核 (Internal Audit)\n   (B) 外部認證稽核\n   (C) 員工滿意度調查\n   (D) 每月一次的資產盤點",
        "7. 關於『適用性聲明 (SoA - Statement of Applicability)』，其主要目的是？\n   (A) 記錄所有員工的簽名\n   (B) 確認哪些 Annex A 控制措施已實施以及排除理由\n   (C) 替代風險評估報告\n   (D) 用於向客戶推廣公司安全性",
        "8. 根據 ISO 19011，當稽核員發現證據不足以證明符合要求時，應如何處理？\n   (A) 直接將其判定為嚴重不符合\n   (B) 嘗試引導受稽核者承認錯誤\n   (C) 記錄事實並在結尾會議中討論，或請求補充證據\n   (D) 忽略該項目，尋找其他證據",
        "9. ISO 27001:2022 中的『持續改善 (Continual Improvement)』對應到 PDCA 循環的哪個階段？\n   (A) Plan\n   (B) Do\n   (C) Check\n   (D) Act",
        "10. 在附錄 A 的『實體控制 (Physical Controls)』中，下列哪項屬於關鍵措施？\n   (A) 密碼複雜度設定\n   (B) 進入受控區域的門禁管理\n   (C) 防火牆規則設定\n   (D) 員工背景調查"
    ]
    
    body_content = "強尼，你好！🐶\n\n這是今天的 ISO 27001:2022 (LAC) 模擬測驗。請嘗試回答以下 10 道題目，完成後請在對話視窗中回覆答案，小白會為你解析！\n\n────────────────────\n"
    body_content += "\n\n".join(questions)
    body_content += "\n\n────────────────────\n加油！祝考試準備順利！"
    
    success = send_email(subject=subject, body=body_content)
    
    if success:
        print("Email sent successfully!")
    else:
        print("Failed to send email. Please check SMTP configuration.")

if __name__ == "__main__":
    main()
