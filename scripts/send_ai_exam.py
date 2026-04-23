import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add scripts directory to sys.path to import send_email
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from send_email import send_email

def main():
    subject = "[AI 應用規劃師] 中級模擬測驗 - 今日挑戰"
    
    questions = [
        "1. 在 AI 技術演進中，Transformer 架構的核心機制是什麼？\n   (A) 遞迴神經網路 (RNN)\n   (B) 注意力機制 (Attention Mechanism)\n   (C) 卷積層 (Convolutional Layer)\n   (D) 梯度下降 (Gradient Descent)",
        "2. 關於 LLM 的 '幻覺' (Hallucination) 現象，下列哪項是最有效的減輕方法？\n   (A) 增加訓練數據量\n   (B) 使用 RAG (檢索增強生成)\n   (C) 提高溫度 (Temperature) 參數\n   (D) 縮短 Prompt 長度",
        "3. 在 AI 專案導入規劃中，定義『成功指標 (Success Metrics)』最適合在哪個階段完成？\n   (A) 資料收集階段\n   (B) 模型微調階段\n   (C) 需求分析與定義階段\n   (D) 部署後維護階段",
        "4. 資料治理 (Data Governance) 的主要目標不包括下列哪一項？\n   (A) 確保資料的正確性與一致性\n   (B) 定義資料的存取權限與安全性\n   (C) 自動化所有資料標記過程\n   (D) 建立資料字典與血緣追蹤",
        "5. 根據 AI 倫理準則，'透明度 (Transparency)' 在 AI 應用中是指什麼？\n   (A) 模型的所有程式碼必須開源\n   (B) 能夠解釋 AI 做出特定決策的邏輯與原因\n   (C) 所有的訓練數據必須公開下載\n   (D) AI 必須能夠即時回應使用者",
        "6. 在評估 AI 專案的 ROI (投資報酬率) 時，下列哪項屬於『間接收益』？\n   (A) 減少人力操作成本\n   (B) 縮短產品開發週期 (Time-to-market)\n   (C) 提高客戶滿意度與品牌忠誠度\n   (D) 增加每單平均客單價",
        "7. 關於 AI 應用場景分析，若企業希望實現『個人化推薦系統』，最關鍵的技術能力是？\n   (A) 零樣本學習 (Zero-shot Learning)\n   (B) 協同過濾或內容基於過濾 (Collaborative/Content Filtering)\n   (C) 強化學習 (Reinforcement Learning)\n   (D) 圖像分割 (Image Segmentation)",
        "8. 在 AI 專案管理中，『MVP (最小可行產品)』的主要目的是？\n   (A) 提供完整功能的最終版本\n   (B) 降低開發成本至最低\n   (C) 快速驗證核心假設並獲取使用者回饋\n   (D) 確保模型達到 99% 的準確率",
        "9. 針對 AI 資安規範，『提示詞注入攻擊 (Prompt Injection Attack)』是指？\n   (A) 透過暴力破解獲取 API Key\n   (B) 誘導 AI 繞過安全限制而產出禁忌內容\n   (C) 針對訓練集進行數據投毒\n   (D) 攻擊伺服器造成拒絕服務 (DoS)",
        "10. 在資料工程基礎中，ETL 流程中的 'T' (Transform) 階段通常包含什麼操作？\n    (A) 從資料庫讀取原始數據\n    (B) 將清洗後的數據寫入 Data Warehouse\n    (C) 數據清洗、格式轉換與聚合\n    (D) 設定 API 請求參數"
    ]
    
    body_content = "強尼，你好！🐶\n\n這是今天的 AI 應用規劃師（中級）模擬測驗。請嘗試回答以下 10 道題目，完成後請在對話視窗中回覆答案，小白會為你解析！\n\n────────────────────\n"
    body_content += "\n\n".join(questions)
    body_content += "\n\n────────────────────\n加油！祝學習愉快！"
    
    success = send_email(subject=subject, body=body_content)
    
    if success:
        print("Email sent successfully!")
    else:
        print("Failed to send email. Please check SMTP configuration.")

if __name__ == "__main__":
    main()
