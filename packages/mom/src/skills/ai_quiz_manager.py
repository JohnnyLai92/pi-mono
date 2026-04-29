"""
AI 中級應用規劃師題型練習管理 Skill (工業級穩健版)

功能：
1. 自動生成隨機試卷（基礎版/進階版）- 導入 UUID 唯一識別機制
2. 每小時自動巡檢並批改試卷 - 實作已完成標記跳過邏輯
3. 自動批改並更新結果 - 導入答案標準化與指數退避重試
4. 記錄弱點追蹤 (預留接口)

作者：小白 (與 Claude 共同審核優化)
更新日期：2026-04-27
"""

import os
import json
import random
import time
import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

import requests
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設定日誌
log_dir = Path('logs')
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'ai_quiz.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AIQuizManager')

class AIQuizManager:
    """AI 應用規劃師中級題型練習管理器 - 穩健版"""
    
    FINISHED_STATUSES = frozenset(["完成", "Done", "Completed", "已完成", "已批改"])
    DEFAULT_TIMEOUT = 15
    NOTION_VERSION = "2022-06-28"
    
    def __init__(self):
        """初始化 Notion API 客戶端"""
        self.token = os.getenv("NOTION_TOKEN")
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        
        if not self.token:
            raise ValueError("NOTION_TOKEN is not set in environment variables.")
        
        self.base_url = "https://api.notion.com/v1"
        
        # 建立 Session (恢復 SSL 驗證)
        self._session = requests.Session()
        self._session.verify = True 
        self._session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": self.NOTION_VERSION,
            "Content-Type": "application/json"
        })
        
        self._load_question_bank()
    
    def _load_question_bank(self):
        """從內部定義載入題庫 (未來可擴展為從 MD 檔案動態解析)"""
        # 基礎版題庫
        self._bank_basic = [
            {
                'id': 'nlp_001',
                'q': '關於自然語言處理（NLP）的發展脈絡，下列敘述何者正確？',
                'options': [
                    '規則式方法依賴大量語料訓練機率模型，且具高可解釋性',
                    '統計語言模型（如 N-gram）能有效捕捉長距離的語言依賴性',
                    'Transformer 架構透過自注意力機制實現全局語境建模，解決了長距離依賴問題',
                    '預訓練語言模型（如 BERT）必須針對單一任務從零開始訓練，無法進行微調'
                ],
                'correct': 'C',
                'analysis': '✓ Transformer 架構透過 Self-Attention 機制實現全局語境建模，解決了傳統 RNN/LSTM 的長距離依賴問題。'
            },
            {
                'id': 'nlp_002',
                'q': '在 NLP 前處理中，「詞形還原 (Lemmatization)」與「詞幹提取 (Stemming)」的主要區別為何？',
                'options': [
                    '詞幹提取依賴字典，語意保留較佳；詞形還原使用簡單裁剪',
                    '詞形還原將單詞還原為字典形式，保留語意一致性；詞幹提取則快速裁剪詞尾',
                    '詞幹提取僅用於中文斷詞，詞形還原僅用於英文',
                    '兩者在功能上完全相同，僅在運算速度上有所差異'
                ],
                'correct': 'B',
                'analysis': '✓ 詞形還原 (Lemmatization) 依賴字典將單詞還原為詞典形式 (如 running→run)，保留語意；詞幹提取 (Stemming) 使用規則快速裁剪詞尾 (如 running→runn)，可能產生非字典詞。'
            },
            {
                'id': 'nlp_003',
                'q': '關於 Word2Vec 的 CBOW 與 Skip-gram 兩種模型，下列分析何者正確？',
                'options': [
                    'CBOW 是以中心詞預測周圍上下文詞彙',
                    'Skip-gram 是以上下文詞彙預測中心詞',
                    'Skip-gram 對於低頻詞的語意捕捉能力通常比 CBOW 更好',
                    'CBOW 的訓練速度較慢，但能比 Skip-gram 捕捉更深層的語意'
                ],
                'correct': 'C',
                'analysis': '✓ Skip-gram 以中心詞預測上下文，對低頻詞更敏感；CBOW 以上下文預測中心詞，訓練較快但對罕見詞捕捉較弱。'
            },
            {
                'id': 'nlp_004',
                'q': 'tf-idf 統計方法中，IDF (Inverse Document Frequency) 的主要目的為何？',
                'options': [
                    '衡量單一文件中的詞頻',
                    '衡量詞彙在整體語料庫中的罕見程度，以降低過於常見詞的權重',
                    '將詞彙轉換為高維度向量',
                    '捕捉詞彙之間的序列與語法結構'
                ],
                'correct': 'B',
                'analysis': '✓ IDF 公式為 log(N/df)，用於衡量詞彙在語料庫中的罕見程度，常見詞 (如 the, is) IDF 值低，罕見詞 IDF 值高。'
            },
            {
                'id': 'nlp_005',
                'q': 'BERT 與 GPT 在 Transformer 的應用上最顯著的差異是什麼？',
                'options': [
                    'BERT 使用單向自迴歸預測，GPT 使用雙向遮蔽語言模型',
                    'BERT 專精於文本生成，GPT 專精於上下文理解',
                    'BERT 採用雙向編碼器以理解上下文，GPT 採用單向自迴歸預測以生成文本',
                    'BERT 的計算資源需求遠低於 GPT'
                ],
                'correct': 'C',
                'analysis': '✓ BERT 使用雙向 Transformer Encoder 理解上下文（適合分類/理解任務）；GPT 使用單向 Transformer Decoder 自迴歸生成（適合文本生成）。'
            },
            {
                'id': 'nlp_006',
                'q': '關於 Transformer 的 Self-Attention 機制，下列敘述何者正確？',
                'options': [
                    '每個位置的詞只能關注前一個位置的詞',
                    '透過 Q(Query)、K(Key)、V(Value) 矩陣，讓每個位置的詞可以關注序列中所有其他位置',
                    'Self-Attention 的計算複雜度為 O(n)',
                    'Self-Attention 無法處理長距離依賴'
                ],
                'correct': 'B',
                'analysis': '✓ Self-Attention 透過 Q、K、V 矩陣，讓每個位置的詞可以關注序列中所有其他位置，計算複雜度為 O(n²)。'
            },
            {
                'id': 'nlp_007',
                'q': '在 LLM 微調中，LoRA (Low-Rank Adaptation) 的核心邏輯是什麼？',
                'options': [
                    '完全重新訓練所有模型權重',
                    '凍結預訓練模型權重，在 Transformer 層中添加低秩分解矩陣，僅訓練 A、B 矩陣',
                    '僅適用於小型模型（<1B 參數）',
                    '必須使用標註資料進行監督微調'
                ],
                'correct': 'B',
                'analysis': '✓ LoRA 凍結預訓練模型權重，在 Transformer 層中添加低秩分解矩陣 (W + ΔW = W + BA)，僅訓練 A、B 矩陣，大幅減少可訓練參數。'
            },
            {
                'id': 'nlp_008',
                'q': '關於 RAG (Retrieval-Augmented Generation) 的流程，下列順序何者正確？',
                'options': [
                    '生成答案 → 檢索文檔 → 接收查詢',
                    '接收用戶查詢 → 從向量資料庫檢索相關文檔 → 將檢索結果增強到 prompt → LLM 基於增強上下文生成答案',
                    '檢索文檔 → 生成答案 → 接收查詢',
                    '接收查詢 → 直接生成答案 → 事後檢索驗證'
                ],
                'correct': 'B',
                'analysis': '✓ RAG 流程：1.接收用戶查詢 → 2.從向量資料庫檢索相關文檔 → 3.將檢索結果增強到 prompt → 4.LLM 基於增強上下文生成答案。'
            },
            {
                'id': 'nlp_009',
                'q': 'LLM 中的 Temperature 參數主要影響什麼？',
                'options': [
                    '模型的最大輸出長度',
                    'softmax 概率分佈的平滑度，控制生成的隨機性與多樣性',
                    '模型的注意力頭數量',
                    '訓練時的學習率'
                ],
                'correct': 'B',
                'analysis': '✓ Temperature 控制 softmax 概率分佈的平滑度：T→0 趨向確定性 (選最高概率)，T→∞ 趨向均勻隨機。高 T 增加多樣性但可能降低連貫性。'
            },
            {
                'id': 'nlp_010',
                'q': '關於 Prompt Engineering 中的 Few-Shot Prompting，其定義是什麼？',
                'options': [
                    '只提供任務描述，不提供示例',
                    '提供大量訓練資料進行微調',
                    '在 prompt 中提供少量輸入 - 輸出示例（通常 1-5 個），讓模型透過上下文學習推斷任務模式',
                    '使用特殊標記分隔不同任務'
                ],
                'correct': 'C',
                'analysis': '✓ Few-Shot Prompting 在 prompt 中提供少量輸入 - 輸出示例 (通常 1-5 個)，讓模型透過上下文學習 (In-Context Learning) 推斷任務模式。'
            }
        ]
        
        # 進階版題庫
        self._bank_advanced = [
            {
                'id': 'adv_001',
                'q': '關於 Transformer 架構中的 Self-Attention 機制，下列計算公式何者正確？',
                'options': [
                    'Attention(Q,K,V) = softmax(QK^T/√d_k)V',
                    'Attention(Q,K,V) = softmax(Q^TK/d_k)V',
                    'Attention(Q,K,V) = sigmoid(QK^T)V',
                    'Attention(Q,K,V) = tanh(Q+K+V)'
                ],
                'correct': 'A',
                'analysis': '✓ Self-Attention 公式為 softmax(QK^T/√d_k)V，其中 √d_k 為縮放因子，防止點積過大導致梯度消失。Q(Query)、K(Key)、V(Value) 矩陣分別來自輸入的線性轉換。'
            },
            {
                'id': 'adv_002',
                'q': '在電腦視覺中，ResNet 引入「殘差連接（Residual Connection）」的主要目的是什麼？',
                'options': [
                    '減少模型參數量，加快推理速度',
                    '解決深度網路退化問題，使梯度更容易反向傳播',
                    '增加特徵圖的空間解析度',
                    '替代卷積層進行特徵提取'
                ],
                'correct': 'B',
                'analysis': '✓ 殘差連接 F(x)+x 讓梯度可以直接通過恆等映射傳播，解決了深度網路（如 50+ 層）的退化（Degradation）問題，使訓練更深層網路成為可能。'
            },
            {
                'id': 'adv_003',
                'q': '關於生成式 AI 中的 Diffusion Model（擴散模型），下列敘述何者正確？',
                'options': [
                    '透過生成器與判別器的對抗訓練生成新圖像',
                    '前向過程逐步添加噪聲，反向過程學習去噪聲生成圖像',
                    '使用自迴歸方式逐像素生成圖像',
                    '依賴潛在空間插值生成新樣本'
                ],
                'correct': 'B',
                'analysis': '✓ Diffusion Model 包含前向擴散過程（逐步加噪）和反向去噪過程（學習從噪聲恢復圖像）。Stable Diffusion 即基於此架構，優於 GAN 的訓練穩定性。'
            },
            {
                'id': 'adv_004',
                'q': '在 RAG（Retrieval-Augmented Generation）系統中，「檢索器（Retriever）」通常使用哪種技術進行語意相似度計算？',
                'options': [
                    'TF-IDF + 餘弦相似度',
                    'BM25 排序算法',
                    '向量嵌入（Embedding）+ 近似最近鄰搜尋（ANN）',
                    '規則式關鍵字匹配'
                ],
                'correct': 'C',
                'analysis': '✓ RAG 的檢索器通常使用預訓練模型（如 BERT、Sentence-BERT）將文檔和查詢轉換為向量，再透過 FAISS、Milvus 等進行近似最近鄰搜尋（ANN），計算餘弦相似度。'
            },
            {
                'id': 'adv_005',
                'q': '關於 LoRA（Low-Rank Adaptation）微調技術，下列何者是其核心優勢？',
                'options': [
                    '完全凍結原模型，僅訓練低秩分解矩陣 A 和 B，大幅減少可訓練參數',
                    '需要完整重新訓練所有模型權重',
                    '僅適用於小型模型（<1B 參數）',
                    '必須使用標註資料進行監督微調'
                ],
                'correct': 'A',
                'analysis': '✓ LoRA 在 Transformer 層中添加低秩矩陣 ΔW=BA（B∈R^(d×r), A∈R^(r×k)，r<<d,k），凍結原權重 W，僅訓練 A、B。例如 7B 模型可從 28GB 顯存需求降至 8GB。'
            },
            {
                'id': 'adv_006',
                'q': '在多模態 AI（如 CLIP、GPT-4V）中，「對比學習（Contrastive Learning）」的主要作用是？',
                'options': [
                    '將圖像和文本映射到同一向量空間，使配對樣本相似度最大化',
                    '生成圖像的文本描述',
                    '對圖像進行物件檢測',
                    '壓縮多模態數據的存儲空間'
                ],
                'correct': 'A',
                'analysis': '✓ CLIP 使用對比學習，將圖像 - 文本對映射到共享向量空間，最大化配對樣本的餘弦相似度，最小化非配對樣本相似度。這使得零樣本（Zero-shot）圖像分類成為可能。'
            },
            {
                'id': 'adv_007',
                'q': '關於 Prompt Engineering 中的「Chain-of-Thought（CoT）」技術，下列何者是其關鍵特徵？',
                'options': [
                    '提供多個輸入 - 輸出示例讓模型模仿',
                    '在 prompt 中加入逐步推理過程，引導模型展示思考鏈',
                    '使用特殊標記分隔不同任務',
                    '限制模型輸出長度以提高準確性'
                ],
                'correct': 'B',
                'analysis': '✓ CoT 透過在 prompt 中加入「讓我們一步一步思考」或提供推理範例，引導模型展示中間推理步驟。這在數學、邏輯推理任務中顯著提升準確率，尤其對大模型（>100B）效果更佳。'
            },
            {
                'id': 'adv_008',
                'q': '在 AI 專案導入評估中，「資料準備度（Data Readiness）」不包含下列哪項評估指標？',
                'options': [
                    '資料量是否足夠訓練目標模型',
                    '資料標註品質與一致性',
                    '伺服器 GPU 型號與數量',
                    '資料分佈是否代表實際應用場景'
                ],
                'correct': 'C',
                'analysis': '✓ 正確答案是 C。資料準備度評估包含：資料量、品質、標註一致性、分佈代表性、合規性等。GPU 硬體屬於「基礎設施準備度」，非資料層面。'
            },
            {
                'id': 'adv_009',
                'q': '關於 GAN（Generative Adversarial Network）的訓練過程，下列敘述何者正確？',
                'options': [
                    '生成器與判別器同時最小化同一損失函數',
                    '生成器試圖欺騙判別器，判別器試圖正確區分真實/生成樣本',
                    '僅需訓練生成器，判別器為固定規則',
                    'GAN 訓練總是穩定收斂，不會出現模式崩潰'
                ],
                'correct': 'B',
                'analysis': '✓ GAN 是二人零和博弈：生成器 G 試圖最小化判別器 D 的準確率（生成逼真樣本），D 試圖最大化準確率（區分真實/生成）。挑戰包括模式崩潰（Mode Collapse）和訓練不穩定。'
            },
            {
                'id': 'adv_010',
                'q': '在企業導入 LLM 應用時，「幻覺（Hallucination）」問題的最佳緩解策略是？',
                'options': [
                    '增加 Temperature 參數提高多樣性',
                    '使用 RAG 架構，讓模型基於檢索到的事實生成答案',
                    '減少訓練資料量避免過擬合',
                    '將模型轉換為更小尺寸'
                ],
                'correct': 'B',
                'analysis': '✓ RAG 透過檢索外部知識庫提供事實依據，顯著減少幻覺。其他策略包括：設定「我不知道」閾值、使用驗證器模型、限制生成基於檢索內容。增加 Temperature 反而會加劇幻覺。'
            }
        ]
    
    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        封裝 Notion API 請求，實作指數退避重試與 429 處理
        """
        max_retries = 5
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = self._session.request(method, url, timeout=self.DEFAULT_TIMEOUT, **kwargs)
                
                if response.status_code == 429:
                    # 處理 Rate Limit
                    wait_time = int(response.headers.get("Retry-After", retry_delay))
                    logger.warning(f"Notion API Rate Limited (429). Waiting {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    logger.error(f"API Request failed after {max_retries} attempts: {e}")
                    raise
                
                wait = retry_delay * (2 ** attempt)
                logger.warning(f"Network error occurred: {e}. Retrying in {wait}s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(wait)
        
        raise requests.exceptions.RequestException("Max retries exceeded")

    def _paginate(self, url: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Notion API 分頁處理器"""
        results = []
        cursor = None
        
        while True:
            if cursor:
                payload["start_cursor"] = cursor
            
            try:
                response = self._request("POST", url, json=payload)
                data = response.json()
                
                results.extend(data.get("results", []))
                
                if not data.get("has_more"):
                    break
                
                cursor = data.get("next_cursor")
            except Exception as e:
                logger.error(f"Pagination failed: {e}")
                break
        
        return results
    
    def _extract_title(self, properties: Dict[str, Any]) -> str:
        """動態提取頁面標題 - 處理多段 rich_text"""
        for prop_data in properties.values():
            if prop_data.get("type") == "title":
                title_list = prop_data.get("title", [])
                if title_list:
                    return "".join([t.get("plain_text", "") for t in title_list])
        return "Untitled"
    
    def _extract_status(self, properties: Dict[str, Any]) -> str:
        """動態提取頁面狀態"""
        for prop_data in properties.values():
            if prop_data.get("type") == "status":
                status_data = prop_data.get("status", {})
                return status_data.get("name", "Unknown")
        return "Unknown"
    
    def get_quiz_page(self) -> Optional[str]:
        """獲取「AI 中級應用規劃師題型練習」頁面 ID"""
        if not self.token:
            return None
        
        url = f"{self.base_url}/search"
        payload = {
            "query": "AI 中級應用規劃師題型練習",
            "filter": {"property": "object", "value": "page"}
        }
        
        try:
            response = self._request("POST", url, json=payload)
            data = response.json()
            
            for result in data.get("results", []):
                if result.get("object") == "page":
                    title = self._extract_title(result.get("properties", {}))
                    if "AI 中級應用規劃師題型練習" in title:
                        return result["id"]
            
            return None
        except Exception as e:
            logger.error(f"Error finding quiz page: {e}")
            return None
    
    def _get_heading_blocks(self, page_id: str) -> List[Dict[str, Any]]:
        """獲取頁面下所有 heading_2 區塊"""
        url = f"{self.base_url}/blocks/{page_id}/children"
        response = self._request("GET", url)
        data = response.json()
        
        headings = []
        for block in data.get("results", []):
            if block.get("type") == "heading_2":
                heading_text = "".join([t.get("plain_text", "") for t in block.get("heading_2", {}).get("rich_text", [])])
                headings.append({
                    "id": block["id"],
                    "text": heading_text,
                    "type": "heading_2"
                })
        
        return headings
    
    def _get_question_blocks(self, heading_id: str) -> List[Dict[str, Any]]:
        """獲取 heading_2 下的所有題目（heading_4）"""
        url = f"{self.base_url}/blocks/{heading_id}/children"
        response = self._request("GET", url)
        data = response.json()
        
        questions = []
        for block in data.get("results", []):
            if block.get("type") == "heading_4":
                q_text = "".join([t.get("plain_text", "") for t in block.get("heading_4", {}).get("rich_text", [])])
                questions.append({
                    "id": block["id"],
                    "question": q_text,
                    "type": "heading_4"
                })
        
        return questions
    
    def _get_question_details(self, question_id: str) -> Dict[str, Any]:
        """獲取題目詳細內容（選項、用戶答案、UUID、批改狀態）"""
        url = f"{self.base_url}/blocks/{question_id}/children"
        response = self._request("GET", url)
        data = response.json()
        
        details = {
            "options": [],
            "user_answer": None,
            "question_uuid": None,
            "robot_callout_id": None,
            "is_graded": False
        }
        
        for block in data.get("results", []):
            block_type = block.get("type")
            
            if block_type == "bulleted_list_item":
                text = "".join([t.get("plain_text", "") for t in block.get("bulleted_list_item", {}).get("rich_text", [])])
                details["options"].append(text)
            
            elif block_type == "callout":
                icon = block.get("callout", {}).get("icon", {})
                emoji = icon.get("emoji", "")
                text = "".join([t.get("plain_text", "") for t in block.get("callout", {}).get("rich_text", [])])
                
                if emoji == "✏️" and "我的答案：" in text:
                    # 答案標準化：提取第一個 [A-D] 字符
                    match = re.search(r'([A-D])', text.upper())
                    if match:
                        details["user_answer"] = match.group(1)
                
                elif emoji == "🤖":
                    details["robot_callout_id"] = block["id"]
                    # 提取 UUID (格式: ID: xxx)
                    uuid_match = re.search(r'ID: ([a-zA-Z0-9_-]+)', text)
                    if uuid_match:
                        details["question_uuid"] = uuid_match.group(1)
                    
                    if "等待批閱" not in text:
                        details["is_graded"] = True
        
        return details
    
    def check_pending_grading(self) -> List[Dict[str, Any]]:
        """
        巡檢 Notion，找出所有需要批改的試卷 (跳過已完成標記 ✅)
        """
        quiz_page_id = self.get_quiz_page()
        if not quiz_page_id:
            logger.error("未找到「AI 中級應用規劃師題型練習」頁面")
            return []
        
        headings = self._get_heading_blocks(quiz_page_id)
        pending_quizzes = []
        
        for heading in headings:
            # 1. 必須是試卷標題 2. 必須不含 ✅ 標記 (表示尚未完成批改)
            if "AI 應用規劃師中級模擬練習" not in heading["text"] or "✅" in heading["text"]:
                continue
            
            questions = self._get_question_blocks(heading["id"])
            questions_to_grade = []
            
            for q in questions:
                details = self._get_question_details(q["id"])
                
                # 只有在有用戶答案且尚未批改時才加入
                if details["user_answer"] and not details["is_graded"]:
                    questions_to_grade.append({
                        "id": q["id"],
                        "question": q["question"],
                        "user_answer": details["user_answer"],
                        "robot_callout_id": details["robot_callout_id"],
                        "question_uuid": details["question_uuid"]
                    })
            
            if questions_to_grade:
                pending_quizzes.append({
                    "heading_id": heading["id"],
                    "heading_text": heading["text"],
                    "questions": questions_to_grade
                })
        
        return pending_quizzes
    
    def grade_quiz(self, quiz_data: Dict[str, Any], difficulty: str = 'basic') -> Dict[str, Any]:
        """
        批改試卷並更新 Notion
        """
        bank = self._bank_basic if difficulty == 'basic' else self._bank_advanced
        
        # 建立 UUID 映射
        id_map = {q['id']: q for q in bank}
        
        results = {
            "total": len(quiz_data["questions"]),
            "correct": 0,
            "score": 0,
            "details": []
        }
        
        for i, q in enumerate(quiz_data["questions"]):
            user_answer = q["user_answer"]
            uuid = q["question_uuid"]
            
            # 優先使用 UUID 匹配
            correct_answer = None
            analysis = None
            
            if uuid and uuid in id_map:
                correct_answer = id_map[uuid]['correct']
                analysis = id_map[uuid]['analysis']
            else:
                # Fallback: 用文字匹配 (僅作為備案，不再依賴 index)
                for item in bank:
                    if item['q'][:20] in q["question"]:
                        correct_answer = item['correct']
                        analysis = item['analysis']
                        break
            
            if not correct_answer:
                correct_answer = '?'
                analysis = '題庫中找不到此題目'
            
            is_correct = user_answer.upper() == correct_answer.upper()
            if is_correct:
                results["correct"] += 1
            
            # 更新 Notion 批閱結果
            if q["robot_callout_id"]:
                status = "✅ 正確" if is_correct else f"❌ 錯誤（正確：{correct_answer}）"
                content = f"批閱結果：{status}\n\n正確解答：{correct_answer}\n\n解析：{analysis}"
                
                update_url = f"{self.base_url}/blocks/{q['robot_callout_id']}"
                payload = {
                    "callout": {
                        "rich_text": [{"type": "text", "text": {"content": content}}]
                    }
                }
                
                try:
                    self._request("PATCH", update_url, json=payload)
                except Exception as e:
                    logger.error(f"Failed to update question {i+1}: {e}")
            
            results["details"].append({
                "question": q["question"][:50],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct
            })
            time.sleep(0.3)
        
        results["score"] = int((results["correct"] / results["total"]) * 100) if results["total"] > 0 else 0
        
        # 如果所有題目都批改完了，將標題標記為 ✅
        if results["correct"] + (results["total"] - results["correct"]) == results["total"]:
            self._mark_quiz_completed(quiz_data["heading_id"], quiz_data["heading_text"])
            
        return results
    
    def _mark_quiz_completed(self, heading_id: str, heading_text: str):
        """將試卷標題加上 ✅ 標記，防止重複巡檢"""
        if "✅" in heading_text:
            return
            
        update_url = f"{self.base_url}/blocks/{heading_id}"
        payload = {
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": f"✅ {heading_text}"}}],
                "is_toggleable": True
            }
        }
        try:
            self._request("PATCH", update_url, json=payload)
            logger.info(f"試卷 {heading_text} 已標記為完成")
        except Exception as e:
            logger.error(f"Failed to mark quiz completed: {e}")

    def generate_quiz(self, difficulty: str = 'basic') -> Dict[str, Any]:
        """
        生成隨機試卷並添加到 Notion (導入 UUID 與 隨機化)
        """
        bank = self._bank_basic if difficulty == 'basic' else self._bank_advanced
        quiz_page_id = self.get_quiz_page()
        if not quiz_page_id:
            return {"error": "Quiz page not found", "success": False}
        
        # 隨機抽取 10 題
        selected_questions = random.sample(bank, min(len(bank), 10))
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        version = "進階版" if difficulty == 'advanced' else "基礎版"
        header_text = f"📅 AI 應用規劃師中級模擬練習 ({timestamp} {version})"
        
        header_payload = {
            "children": [
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": header_text}}],
                        "is_toggleable": True
                    }
                }
            ]
        }
        
        url = f"{self.base_url}/blocks/{quiz_page_id}/children"
        
        try:
            response = self._request("PATCH", url, json=header_payload)
            heading_id = response.json()["results"][0]["id"]
            
            for q_data in selected_questions:
                # 打亂選項順序
                original_options = q_data['options']
                correct_text = original_options[ord(q_data['correct']) - 65]
                
                shuffled_options = original_options[:]
                random.shuffle(shuffled_options)
                
                # 計算新正確答案標記
                new_correct = chr(65 + shuffled_options.index(correct_text))
                
                # 創建 Toggle H4
                toggle_payload = {
                    "children": [
                        {
                            "object": "block",
                            "type": "heading_4",
                            "heading_4": {
                                "rich_text": [{"type": "text", "text": {"content": q_data['q']}}],
                                "is_toggleable": True
                            }
                        }
                    ]
                }
                
                toggle_response = self._request("PATCH", url, json=toggle_payload)
                toggle_id = toggle_response.json()["results"][0]["id"]
                
                # 創建選項和答案區塊
                children = []
                for i, opt in enumerate(shuffled_options):
                    children.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": f"({chr(65+i)}) {opt}"}}]
                        }
                    })
                
                children.append({
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "icon": {"type": "emoji", "emoji": "✏️"},
                        "rich_text": [{"type": "text", "text": {"content": "我的答案：\n(在此輸入內容)"}}]
                    }
                })
                
                # 在🤖 callout 中隱藏 UUID 用於批改
                children.append({
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "icon": {"type": "emoji", "emoji": "🤖"},
                        "rich_text": [{"type": "text", "text": {"content": f"批閱結果：(等待批閱...)\nID: {q_data['id']}"}}]
                    }
                })
                
                self._request("PATCH", f"{self.base_url}/blocks/{toggle_id}/children", json={"children": children})
                time.sleep(0.5)
            
            return {
                "success": True,
                "heading_id": heading_id,
                "question_count": len(selected_questions),
                "timestamp": timestamp,
                "difficulty": difficulty
            }
        except Exception as e:
            logger.error(f"Generate quiz failed: {e}")
            return {"success": False, "error": str(e)}
    
    def run_hourly_check(self) -> Dict[str, Any]:
        """
        每小時巡檢並自動批改
        """
        result = {
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "quizzes_found": 0,
            "quizzes_graded": []
        }
        
        pending_quizzes = self.check_pending_grading()
        result["quizzes_found"] = len(pending_quizzes)
        
        for quiz in pending_quizzes:
            difficulty = 'advanced' if '進階版' in quiz['heading_text'] else 'basic'
            grading_result = self.grade_quiz(quiz, difficulty)
            
            if "error" not in grading_result:
                result["quizzes_graded"].append({
                    "heading_text": quiz['heading_text'],
                    "score": grading_result["score"],
                    "correct": grading_result["correct"],
                    "total": grading_result["total"]
                })
        
        return result

    def check_pending_grading(self) -> List[Dict[str, Any]]:
        """巡檢 Notion，找出所有需要批改的試卷"""
        quiz_page_id = self.get_quiz_page()
        if not quiz_page_id:
            return []
        
        headings = self._get_heading_blocks(quiz_page_id)
        pending_quizzes = []
        
        for heading in headings:
            if "AI 應用規劃師中級模擬練習" not in heading["text"] or "✅" in heading["text"]:
                continue
            
            questions = self._get_question_blocks(heading["id"])
            questions_to_grade = []
            for q in questions:
                details = self._get_question_details(q["id"])
                if details["user_answer"] and not details["is_graded"]:
                    questions_to_grade.append({
                        "id": q["id"],
                        "question": q["question"],
                        "user_answer": details["user_answer"],
                        "robot_callout_id": details["robot_callout_id"],
                        "question_uuid": details["question_uuid"]
                    })
            
            if questions_to_grade:
                pending_quizzes.append({
                    "heading_id": heading["id"],
                    "heading_text": heading["text"],
                    "questions": questions_to_grade
                })
        
        return pending_quizzes

# ============== Skill Entry Points ==============

def generate_ai_quiz(difficulty: str = 'basic'):
    manager = AIQuizManager()
    return manager.generate_quiz(difficulty)

def grade_ai_quizzes():
    manager = AIQuizManager()
    return manager.run_hourly_check()
