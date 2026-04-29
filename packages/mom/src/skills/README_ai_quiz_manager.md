# AI 中級應用規劃師題型練習管理 Skill

## 📋 功能概述

此 Skill 提供完整的 AI 應用規劃師中級考試練習題管理功能：

1. **自動生成試卷**：可生成基礎版（NLP 為主）或進階版（跨領域）試卷
2. **每小時自動巡檢**：檢查 Notion 中有無用戶已作答但未批改的試卷
3. **自動批改**：批改試卷並立即更新 Notion 頁面
4. **弱點追蹤**：記錄答錯題目（未來擴展功能）

## 🔧 環境變數設定

確保 `.env` 檔案中包含以下必要參數：

```env
NOTION_TOKEN=ntn_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 📖 使用方式

### 方法 1: 手動生成試卷

```python
from skills.ai_quiz_manager import generate_ai_quiz

# 生成基礎版試卷（NLP 主題，10 題）
generate_ai_quiz('basic')

# 生成進階版試卷（CV、生成式 AI、多模態等，10 題）
generate_ai_quiz('advanced')
```

### 方法 2: 手動批改試卷

```python
from skills.ai_quiz_manager import grade_ai_quizzes

# 巡檢並批改所有待批改試卷
grade_ai_quizzes()
```

### 方法 3: 排程自動執行

#### 設定每小時自動批改

在 `pi_scheduler` 或系統排程中加入：

```python
# 每小時整點執行
from skills.ai_quiz_manager import AIQuizManager

manager = AIQuizManager()
result = manager.run_hourly_check()

# 如果有批改結果，可選擇發送 Email 或 LINE 通知
if result['quizzes_graded']:
    send_notification(result)
```

#### 設定每日自動生成試卷

```python
# 每天早上 8:00 生成新試卷
from skills.ai_quiz_manager import generate_ai_quiz
from datetime import datetime

# 單數日生成基礎版，雙數日生成進階版
day = datetime.now().day
difficulty = 'basic' if day % 2 == 1 else 'advanced'

generate_ai_quiz(difficulty)
```

## 📊 Notion 頁面結構要求

### 目標頁面
- **頁面名稱**：`AI 中級應用規劃師題型練習`
- **頁面類型**：Notion Page（非 Database）
- **存取權限**：需授予 Integration 編輯權限

### 試卷結構

```
📅 AI 應用規劃師中級模擬練習 (2026-04-27 基礎版)  [Heading 2, 可收摺]
├─ 題目 1：關於自然語言處理...  [Heading 4, 可收摺]
│  ├─ (A) 選項內容...  [Bulleted List]
│  ├─ (B) 選項內容...  [Bulleted List]
│  ├─ (C) 選項內容...  [Bulleted List]
│  ├─ (D) 選項內容...  [Bulleted List]
│  ├─ ✏️ 我的答案：A  [Callout]
│  └─ 🤖 批閱結果：✅ 正確...  [Callout]
├─ 題目 2：...  [Heading 4]
│  └─ ...
└─ ...（共 10 題）
```

## 🎯 試卷內容

### 基礎版（NLP 主題）
涵蓋範圍：
- NLP 發展脈絡
- 詞形還原 vs 詞幹提取
- Word2Vec (CBOW/Skip-gram)
- tf-idf
- BERT vs GPT
- Self-Attention 機制
- LoRA 微調
- RAG 流程
- Temperature 參數
- Few-Shot Prompting

### 進階版（跨領域主題）
涵蓋範圍：
- Self-Attention 數學公式
- ResNet 殘差連接（電腦視覺）
- Diffusion Model（生成式 AI）
- RAG 檢索器技術
- LoRA 核心優勢
- 對比學習（多模態 AI）
- Chain-of-Thought Prompting
- AI 專案導入評估
- GAN 訓練機制
- LLM 幻覺問題緩解

## 🔄 自動批改邏輯

1. **巡檢**：每小時檢查 `AI 中級應用規劃師題型練習` 頁面
2. **識別試卷**：找出所有 Heading 2 中包含「AI 應用規劃師中級模擬練習」的區塊
3. **檢查作答**：對每個試卷：
   - 讀取所有 Heading 4（題目）
   - 檢查 `✏️` Callout 中是否有用戶答案（非空且非預設文字）
   - 檢查 `🤖` Callout 中是否為「等待批閱...」狀態
4. **批改**：
   - 匹配題庫中的正確答案
   - 判斷對錯
   - 生成解析文字
5. **更新 Notion**：
   - 更新 `🤖` Callout 內容為批改結果
   - 格式：`批閱結果：✅ 正確 / ❌ 錯誤（正確：X）\n\n正確解答：X\n\n解析：...`
6. **回報**：回傳批改統計結果

## 📈 弱點追蹤（未來擴展）

```python
# 未來可擴展功能
def track_weaknesses(grading_result):
    """記錄答錯題目到弱點資料庫"""
    weaknesses = []
    
    for detail in grading_result['details']:
        if not detail['is_correct']:
            weaknesses.append({
                'question': detail['question'],
                'topic': extract_topic(detail['question']),
                'wrong_answer': detail['user_answer'],
                'correct_answer': detail['correct_answer'],
                'timestamp': datetime.now().isoformat()
            })
    
    # 寫入資料庫或檔案
    save_weaknesses(weaknesses)
    
    # 安排間隔重複練習 (T+1, T+3, T+7)
    schedule_review(weaknesses)
```

## 🐛 錯誤處理

### 常見錯誤與解決方案

| 錯誤訊息 | 原因 | 解決方案 |
|----------|------|----------|
| `NOTION_TOKEN is not set` | 環境變數未設定 | 檢查 `.env` 檔案是否存在且包含 `NOTION_TOKEN` |
| `Quiz page not found` | 找不到目標頁面 | 確認頁面名稱為「AI 中級應用規劃師題型練習」且 Integration 有權限 |
| `Pagination failed` | Notion API 連線問題 | 檢查網路連線，增加 `DEFAULT_TIMEOUT` |
| `Failed to update question` | 區塊權限不足 | 確認 Integration 有編輯該頁面的權限 |

## 📝 日誌記錄

建議在生產環境中加入日誌記錄：

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ai_quiz_manager.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('AIQuizManager')
```

## 🔐 安全性注意事項

1. **API Token 保護**：
   - 絕不將 `NOTION_TOKEN` 提交到版本控制
   - 使用 `.env` 檔案並加入 `.gitignore`

2. **權限最小化**：
   - Notion Integration 僅授予必要頁面的「編輯」權限
   - 不授予整個 Workspace 的權限

3. **速率限制**：
   - 每次 API 呼叫間隔至少 0.3 秒
   - 大量操作時實作指數退避（Exponential Backoff）

## 📞 支援與維護

- **作者**：小白
- **建立日期**：2026-04-27
- **最後更新**：2026-04-27
- **問題回報**：請聯繫強尼（Johnny）

## 🚀 未來改進計畫

- [ ] 增加題庫來源（從 iPAS Markdown 檔案自動解析）
- [ ] 實作弱點追蹤與間隔重複練習排程
- [ ] 增加多益英文、ISO 27001 等其他考試類型
- [ ] 整合 Email 通知功能（批改完成後自動寄送成績單）
- [ ] 增加統計報表（正確率趨勢、弱項分析圖表）
