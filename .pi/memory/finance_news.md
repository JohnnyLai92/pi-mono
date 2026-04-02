# 每天早上推播國際財經 10 大新聞

## 目標
協助強尼（Johnny）在每天早上 7:30，自動整理前一日的國際財經新聞，並透過小黃（LineBot）推播給強尼。

## 執行規則
- **觸發時間**：每天 07:30（Asia/Taipei）
- **流程**：
  1. `pi_scheduler` 透過 `pi agent` 抓取前一日的財經新聞原始資料（包含 DuckDuckGo 與 RSS 來源）。
  2. `pi agent` 進行統整，產生國際財經 10 大重要新聞，包含股市、匯率、原物料、總體經濟等面向。
  3. 產出結果後，直接 POST 到 LineBot 的 `/push` 端點。
  4. LineBot 接收到文字後，直接傳送 LINE 推播訊息給強尼，不再卡用 LineBot 的資源。

## 備註
- 此功能移除了 LineBot 內建的 APScheduler，改由 `pi_scheduler`（或 pi agent 排程）統一觸發。
- 建立日期：2026-04-02
