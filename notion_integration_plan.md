# Notion 整合規劃指南

## 1. 目標
將 Notion 作為強尼（Johnny）的知識管理中心與長期儲存備份，透過小白將各項任務（財經新聞、考試練習、每日決策）自動同步至 Notion 資料庫。

## 2. 整合步驟

### 第一步：環境準備
1.  **Notion API 申請**：
    - 前往 [Notion Developers](https://www.developers.notion.com/) 建立新的 Integration。
    - 取得 `Internal Integration Token`。
2.  **建立資料庫 (Database)**：
    - 在 Notion 中建立一個新頁面，並新增一個「Database」。
    - 將此 Database 分享給上述建立的 Integration。
    - 記下 Database ID（網址中 `?v=` 前面的一串 ID）。
3.  **環境設定**：
    - 將 `NOTION_TOKEN` 與 `NOTION_DATABASE_ID` 加入系統的 `.env` 檔案中。

### 第二步：開發串接模組
1.  **安裝 SDK**：在 `packages/` 下安裝 `@notionhq/client`。
2.  **建立 Notion 處理程式**：
    - 建立 `scripts/notion_sync.py`（或整合至現有指令）。
    - 定義將 Markdown 內容轉換為 Notion Blocks 的邏輯。
    - 定義上傳 API 請求。

### 第三步：流程整合
1.  **每日新聞整合**：修改 `pi_scheduler.py` 中的 `task_finance_news`，在寄送或推播的同時，自動將新聞內容新增至 Notion 的「財經日誌」資料庫。
2.  **學習成績記錄**：修改 AI 與 ISO 練習題的驗收邏輯，將強尼的回答與解析同步至 Notion 的「學習記錄」資料庫。
3.  **記憶彙整自動化**：將每日 17:00 的 `consolidate_memory` 摘要直接同步至 Notion 的「今日總結」頁面。

### 第四步：自動化與測試
1.  **測試腳本**：執行 `python scripts/notion_sync.py --test` 確認連線。
2.  **排程掛載**：將同步邏輯整合進 `pi_scheduler.py` 的任務迴圈。
3.  **驗收**：觀察 24 小時內的同步狀況，修正 Notion API 回傳的錯誤處理邏輯。

## 3. 注意事項
- **格式限制**：Notion API 的 Block 格式嚴謹，需先定義良好的 Markdown to Notion Block 對應映射表。
- **安全性**：Token 嚴禁直接寫入程式碼，務必使用 `.env` 管理。
- **維護性**：若 Notion 資料庫 Schema 變更，需同步更新 `notion_sync.py` 中的 Property 對應。

---
建立日期：2026-04-23
