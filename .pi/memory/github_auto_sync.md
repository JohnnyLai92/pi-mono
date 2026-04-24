# 每小時自動同步 GitHub 專案 (pi-mono)

## 目標
協助強尼（Johnny）每小時自動將 `pi-mono` 專案中的差異檔案提交（Commit）並推播（Push）到 GitHub，確保雲端備份的即時性。

## 執行規則
- **頻率**：每小時一次。
- **對話中限制**：**當強尼正在與小白對話時，必須暫停/停用同步排程，以避免中斷對話流程或在不完整狀態下提交代碼。**
- **流程**：
  1. 檢查 `C:\Projects\github\pi-mono` 目錄下是否有變更（修改、新增、刪除的檔案）。
  2. 若有變更，自動執行 `git add .`（或只加入強尼修改的檔案）。
  3. 產生帶有時間戳記的 Commit 訊息，例如：`Auto-sync: [YYYY-MM-DD HH:MM:SS]`。
  4. 執行 `git push origin main` 將變更同步到 GitHub。
- **實現方式**：
  - 由於小白無法自行在背景常駐執行定時任務，此功能需透過 Windows 排程工作（Task Scheduler）搭配批次檔（.bat）或 Shell Script 來實現自動化。

## 備註
- 建立日期：2026-04-02