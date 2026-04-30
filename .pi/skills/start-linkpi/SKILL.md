---
name: start_linkpi
description: 啟動 LinkPi 伺服器，綁定 0.0.0.0:8765，提供 LLM API 橋接功能。
---

# 啟動 LinkPi 伺服器

## 描述
用於在背景啟動 `LinkPi.py`，這是一個相容 OpenAI API 格式的 HTTP Bridge，並將執行日誌輸出到 `linkpi.log` 中。

## 使用時機
當強尼（使用者）要求「啟動 LinkPi」或「執行 LinkPi.py」時使用此技能。

## 執行步驟
1. 確認當前工作目錄下存在 `LinkPi.py` 檔案。
2. 執行以下 Bash 指令來在背景啟動伺服器：
   ```bash
   nohup python LinkPi.py > linkpi.log 2>&1 &
   sleep 2
   cat linkpi.log
   ```
3. 確認終端機輸出顯示伺服器已成功啟動（如 `Uvicorn running on http://127.0.0.1:8765`）。
4. 提示強尼伺服器已啟動，並附上供 OpenCode 使用的 `opencode.json` 設定範例，方便他直接複製使用。
