"""
send_ai_exam.py — 讀取 iPAS/*.md，動態產生 AI 應用規劃師模擬考題並寄發 Email

執行方式：
  python scripts/send_ai_exam.py
"""
import logging
import os
import random
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from send_email import send_email

logger = logging.getLogger(__name__)

_IPAS_DIR = Path(__file__).parent.parent / "iPAS"

# ── 靜態題庫（API 不可用時輪替備援，共 3 組） ────────────────────────────────
_STATIC_SETS = [
    # Set A
    [
        "1. [AI技術應用-NLP] 某電商平台要分析每日數萬則客服對話，自動分類問題類型並偵測負面情緒。下列哪種技術組合最適合？\n   (A) 規則式關鍵字比對 + 固定回應模板\n   (B) 意圖辨識（NLU）+ 情感分析（Sentiment Analysis）\n   (C) 僅使用 N-gram 統計語言模型\n   (D) 圖像辨識 + 語音合成",
        "2. [AI技術應用-電腦視覺] 工廠導入視覺 AI 進行瑕疵品檢測，初期標注資料僅 500 張，訓練後準確率偏低。最合適的改善策略是？\n   (A) 立即採購更昂貴的 GPU 重新訓練\n   (B) 使用資料增強（Data Augmentation）+ 遷移學習（Transfer Learning）\n   (C) 改用純規則式影像處理\n   (D) 增加隱藏層數量至 100 層以上",
        "3. [AI技術應用-生成式AI] 企業想用生成式 AI 自動撰寫行銷文案，但擔心內容不準確。最有效的風險控制方式是？\n   (A) 完全禁止使用生成式 AI\n   (B) 導入 RAG（檢索增強生成），讓模型從企業知識庫擷取事實依據\n   (C) 提高 Temperature 參數讓輸出更多樣\n   (D) 縮短所有 Prompt 長度",
        "4. [大數據-統計] 分析一批員工薪資資料時，發現少數高管薪資極高，導致平均薪資遠高於多數員工實際薪資。在此情境下，哪個統計量最能代表「一般員工」的薪資水準？\n   (A) 算術平均數（Mean）\n   (B) 中位數（Median）\n   (C) 標準差（Standard Deviation）\n   (D) 方差（Variance）",
        "5. [大數據-機率分佈] 醫院統計每天急診室到院人數，歷史資料顯示平均每小時 8 人。若要預測某一特定小時「恰好來 10 人」的機率，應使用哪種分佈？\n   (A) 常態分佈（Normal Distribution）\n   (B) 泊松分佈（Poisson Distribution）\n   (C) 均勻分佈（Uniform Distribution）\n   (D) 二項分佈（Binomial Distribution）",
        "6. [大數據-儲存] 公司需儲存每日產生的 10TB 非結構化日誌資料（JSON 格式），並支援即時查詢分析。下列哪個架構最合適？\n   (A) 單一 MySQL 關聯式資料庫\n   (B) 資料湖（Data Lake）+ 分散式查詢引擎（如 Presto）\n   (C) 僅使用本機 CSV 文字檔\n   (D) 傳統 OLTP 交易型資料庫",
        "7. [機器學習-演算法] 客戶流失預測任務中，正樣本（流失）僅占 5%。直接訓練後模型準確率 95%，但幾乎所有流失客戶都被預測為「不流失」。應優先採取哪個策略？\n   (A) 將模型換成更深的神經網路\n   (B) 採用過採樣（SMOTE）或調整類別權重（class_weight）解決類別不平衡\n   (C) 增加訓練資料總量但維持原始比例\n   (D) 將閾值（Threshold）直接設為 0.95",
        "8. [機器學習-深度學習] 訓練影像分類模型時，訓練集準確率 99%，驗證集準確率僅 62%。這種現象最可能是什麼，應如何處理？\n   (A) 欠擬合（Underfitting），應增加模型複雜度\n   (B) 過擬合（Overfitting），應加入 Dropout 或 L2 正則化\n   (C) 梯度消失，應移除所有 Batch Normalization\n   (D) 學習率過低，應調高至 1.0",
        "9. [機器學習-治理] AI 信用評分系統上線後，被發現對特定族群核貸率明顯偏低。從 AI 治理角度，首要處理步驟是？\n   (A) 立即提高該族群的核貸上限\n   (B) 審查訓練資料的歷史偏見來源，並重新設計公平性指標\n   (C) 只要整體準確率高就無需調整\n   (D) 將模型換成黑箱深度學習以規避法規審查",
        "10. [AI技術應用-導入規劃] 製造業欲導入 AI 視覺檢測取代人工目視，專案規劃師應在哪個階段「定義成功指標（KPI）」？\n   (A) 模型部署並上線後\n   (B) 需求分析與可行性評估階段，與業務部門共同制定\n   (C) 資料收集完成後再決定\n   (D) 等模型訓練完成，看結果再定義",
    ],
    # Set B
    [
        "1. [AI技術應用-多模態] 自駕車系統需同時整合鏡頭影像、雷達點雲與 GPS 訊號進行即時決策。這種整合多種感知來源的 AI 系統屬於哪種技術架構？\n   (A) 單模態深度學習\n   (B) 多模態 AI（Multimodal AI）\n   (C) 純規則式專家系統\n   (D) 強化學習（RL）獨立運作",
        "2. [AI技術應用-NLP] 企業想建立內部知識問答系統，讓員工查詢公司政策文件。相比直接使用通用 LLM，導入 RAG 架構的主要優勢是？\n   (A) 降低模型推論速度\n   (B) 讓模型能即時存取企業私有文件，減少幻覺並提升答案準確性\n   (C) 完全取代向量資料庫的需求\n   (D) 讓模型參數從零開始訓練",
        "3. [大數據-假設檢定] A/B 測試中，新版首頁轉換率 5.2%，舊版 4.8%，p-value = 0.08，顯著水準 α = 0.05。正確的業務決策應是？\n   (A) 立即全量推出新版，差異明顯\n   (B) 無法拒絕虛無假設，差異未達統計顯著，建議延長測試或擴大樣本\n   (C) p-value < 0.1 已足夠，可接受\n   (D) 直接採用效果最好的版本，不需統計檢定",
        "4. [大數據-數據清理] 數據清洗時發現某欄位有 15% 的缺失值（MCAR 機制），且該特徵對預測目標有中等相關性。最適合的處理方式是？\n   (A) 直接刪除整個特徵欄位\n   (B) 使用均值/中位數填補，或以迴歸模型進行插補\n   (C) 將缺失值全部填為 0\n   (D) 直接刪除所有含缺失值的樣本列",
        "5. [大數據-可視化] 業務主管想了解各地區過去 12 個月的銷售趨勢變化，並比較各月份之間的差異。最適合的可視化圖表類型是？\n   (A) 圓餅圖（Pie Chart）\n   (B) 折線圖（Line Chart）或分組長條圖（Grouped Bar Chart）\n   (C) 散佈圖（Scatter Plot）\n   (D) 箱型圖（Box Plot）",
        "6. [機器學習-特徵工程] 訓練房價預測模型，原始特徵包含「建造年份」（1980-2020）。將其轉換為「屋齡 = 2025 - 建造年份」後，模型表現明顯提升。這個操作屬於哪種特徵工程技術？\n   (A) 特徵縮放（Feature Scaling）\n   (B) 特徵衍生（Feature Derivation / Feature Engineering）\n   (C) 主成分分析（PCA）\n   (D) One-Hot 編碼",
        "7. [機器學習-模型評估] 醫療 AI 診斷癌症，False Negative（漏診）代價遠高於 False Positive（誤診）。在選擇評估指標時，應優先最大化哪個指標？\n   (A) 整體準確率（Accuracy）\n   (B) 精確率（Precision）\n   (C) 召回率（Recall / Sensitivity）\n   (D) 特異度（Specificity）",
        "8. [機器學習-深度學習] Transformer 的自注意力機制（Self-Attention）相較於 RNN 的主要架構優勢是？\n   (A) 參數量更少，訓練更快\n   (B) 能並行處理序列中所有位置的關係，解決長距離依賴問題\n   (C) 僅適用於圖像處理任務\n   (D) 不需要大量訓練資料",
        "9. [大數據-隱私合規] 公司計劃將含有姓名、地址的客戶資料用於 AI 模型訓練。為符合個資保護法規（如 GDPR），應優先採取哪項措施？\n   (A) 直接使用原始資料，訓練完成後刪除\n   (B) 進行資料去識別化（De-identification）或匿名化（Anonymization）\n   (C) 僅告知客戶即可，不需實際處理資料\n   (D) 將資料傳輸至法規寬鬆的境外伺服器",
        "10. [AI技術應用-風險管理] 某金融機構部署 AI 信貸審核系統後，發現模型在市場劇烈波動期間預測準確率大幅下降。這種現象稱為什麼，應如何應對？\n   (A) 資料過擬合，應增加訓練資料\n   (B) 模型漂移（Model Drift），應建立持續監控機制並定期重新訓練\n   (C) 硬體效能不足，應升級 GPU\n   (D) 超參數設定錯誤，應重新調參",
    ],
    # Set C
    [
        "1. [AI技術應用-生成式AI] 法律事務所要用 LLM 協助撰寫合約草稿，但擔心模型生成錯誤法條引用。最合適的技術解決方案是？\n   (A) 使用最高 Temperature 值以產生最多元內容\n   (B) 建立法規文件的向量資料庫，搭配 RAG 確保引用內容可溯源\n   (C) 每次人工審閱就不需要任何技術控制\n   (D) 訓練一個新的小型 LLM 從頭學習法律知識",
        "2. [大數據-機率統計] 品管部門對一批 1000 個零件進行抽樣，已知每個零件獨立地有 3% 的缺陷率。抽取 50 個零件時，「恰好有 2 個缺陷品」的機率應使用哪種分佈計算？\n   (A) 泊松分佈\n   (B) 二項分佈（Binomial Distribution）\n   (C) 常態分佈\n   (D) 指數分佈",
        "3. [大數據-大數據分析] 電信公司擁有 5 億筆通話記錄，需要即時分析異常通話模式（如詐騙偵測），延遲要求在 1 秒內。最適合的技術架構是？\n   (A) 夜間批次處理（Batch Processing）\n   (B) 串流處理（Stream Processing），如 Apache Kafka + Flink\n   (C) 每 6 小時執行一次 SQL 報表\n   (D) 手動下載 CSV 後用 Excel 分析",
        "4. [機器學習-基礎數學] 在梯度下降（Gradient Descent）優化中，學習率（Learning Rate）設定過高會導致什麼問題？\n   (A) 訓練速度過慢，需要更多 epoch\n   (B) 損失函數（Loss）無法收斂，參數在最佳解附近震盪甚至發散\n   (C) 模型自動停止訓練\n   (D) 批次大小（Batch Size）自動縮小",
        "5. [機器學習-演算法] 電商平台要為每位用戶推薦商品，訓練資料含大量歷史購買行為。下列哪種方法最適合作為協同過濾（Collaborative Filtering）的基礎？\n   (A) 決策樹（Decision Tree）\n   (B) 矩陣分解（Matrix Factorization），如 SVD\n   (C) K-Means 分群\n   (D) 線性迴歸（Linear Regression）",
        "6. [機器學習-建模] 訓練文字情感分類器時，使用 BERT 預訓練模型進行微調（Fine-tuning），相較於從頭訓練的主要優勢是？\n   (A) BERT 不需要任何訓練資料\n   (B) 利用預訓練的語言知識，用較少標注資料即可達到高效能\n   (C) 微調後模型參數量會大幅減少\n   (D) 完全消除過擬合問題",
        "7. [大數據-機器學習應用] 公司想預測下個季度的銷售額，目前有 3 年的月銷售歷史資料。最適合的模型類型是？\n   (A) 圖像分類 CNN\n   (B) 時間序列預測模型，如 LSTM 或 Prophet\n   (C) 隨機森林分類器\n   (D) K 近鄰法（KNN）",
        "8. [AI技術應用-導入評估] AI 導入規劃師評估是否導入 AI 進行文件審查時，首要確認的是？\n   (A) 購買最新款 GPU 伺服器\n   (B) 業務痛點、現有流程瓶頸，以及是否有足夠的訓練資料\n   (C) 找最便宜的模型供應商\n   (D) 先做 Demo，之後再評估資料需求",
        "9. [機器學習-治理] 模型上線後，如何持續確保模型決策的可解釋性以符合監管要求？\n   (A) 只需在上線前做一次解釋報告\n   (B) 導入 SHAP 或 LIME 等可解釋 AI（XAI）工具，持續監控特徵重要性變化\n   (C) 使用越深的神經網路，可解釋性自然越高\n   (D) 可解釋性與準確率無法兼顧，選準確率即可",
        "10. [大數據-隱私安全] 研究機構欲在不取得原始資料的情況下，讓多個醫院聯合訓練疾病預測模型。最適合的隱私保護 AI 技術是？\n   (A) 集中式學習，將所有資料傳到同一台伺服器\n   (B) 聯邦學習（Federated Learning）\n   (C) 直接用公開資料集替代\n   (D) 差分隱私（Differential Privacy）單獨使用即可",
    ],
]


def _load_ipas_context(max_chars: int = 8000) -> str:
    """從三份 .md 中各隨機抽取段落，組成出題素材"""
    md_files = sorted(_IPAS_DIR.glob("*.md"))
    if not md_files:
        return ""

    excerpts = []
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
            # 以標題切段
            sections = re.split(r"\n#{1,2} ", content)
            sections = [s.strip() for s in sections if len(s.strip()) > 300]
            if not sections:
                continue
            chosen = random.sample(sections, min(2, len(sections)))
            excerpt = "\n\n".join(chosen)[:2500]
            excerpts.append(f"【{md_file.stem[:30]}】\n{excerpt}")
        except Exception:
            continue

    combined = "\n\n---\n\n".join(excerpts)
    return combined[:max_chars]


def _generate_with_api(context: str) -> str:
    """呼叫 Claude API，根據 iPAS 內容動態出題"""
    import anthropic

    client = anthropic.Anthropic()
    prompt = (
        "你是 iPAS AI 應用規劃師（中級）考試的出題委員。\n"
        "根據以下學習指引節錄，設計 10 道「情境分析題」。\n\n"
        "出題規則：\n"
        "1. 每題以實際業務情境出發，考驗應用判斷，避免純定義確認型\n"
        "2. 各題開頭標註：[科目-主題]，科目三選一：AI技術應用、大數據、機器學習\n"
        "3. 三個科目各出 3-4 題，總計 10 題\n"
        "4. 每題附 4 個選項（A/B/C/D），選項須有合理迷惑性\n"
        "5. 不附答案（學習者作答後再給解析）\n"
        "6. 題目編號 1-10\n\n"
        f"參考內容：\n{context}\n\n"
        "請直接輸出 10 道題目，不需前言或說明。"
    )

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def _static_fallback() -> str:
    """靜態題庫輪替（以星期幾選組，確保週間不重複）"""
    day_index = datetime.now().weekday() % len(_STATIC_SETS)
    questions = _STATIC_SETS[day_index]
    return "\n\n".join(questions)


def main() -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    subject = f"[AI 應用規劃師] 中級模擬測驗 {today}"

    questions_text = ""
    source = "靜態題庫"

    if os.getenv("ANTHROPIC_API_KEY") and _IPAS_DIR.exists():
        context = _load_ipas_context()
        if context:
            try:
                questions_text = _generate_with_api(context)
                source = "動態生成（iPAS 指引對齊）"
            except Exception as e:
                logger.warning("API 出題失敗，改用靜態題庫：%s", e)

    if not questions_text:
        questions_text = _static_fallback()

    body = (
        f"強尼，你好！🐶\n\n"
        f"這是今日（{today}）的 iPAS AI 應用規劃師（中級）模擬測驗。\n"
        f"出題方式：{source}\n"
        f"題目涵蓋【AI技術應用】、【大數據】、【機器學習】三大科目。\n\n"
        f"請作答後，在對話視窗中回覆答案，小白會根據官方指引為你詳細解析！\n\n"
        f"{'─' * 44}\n\n"
        f"{questions_text}\n\n"
        f"{'─' * 44}\n"
        f"加油！祝準備順利 🐶"
    )

    ok = send_email(subject=subject, body=body)
    if ok:
        print(f"Email sent: {subject}")
    else:
        print("Failed to send email. Please check SMTP configuration.")


if __name__ == "__main__":
    import logging as _logging
    from dotenv import load_dotenv
    load_dotenv()
    _logging.basicConfig(level=_logging.INFO, format="%(levelname)s: %(message)s")
    main()
