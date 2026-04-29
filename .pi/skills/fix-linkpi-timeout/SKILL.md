---
name: fix-linkpi-timeout 
description: 當強尼在使用 VS Code (OpenCode) 透過 LinkPi 串接 LLM (如 Google Gemini) 時，若遇到第一次對話傳送大量上下文導致超過預設的 15 秒等待上限，就會引發 `TimeoutError`，進而造成 OpenCode 不斷重試並卡住。此技能會教小白如何將 `LinkPi.py` 中的等待上限從 15 秒延長至 60 秒，並重新啟動伺服器
---

# 修正 LinkPi 逾時錯誤 (TimeoutError)

## 描述
當強尼在使用 VS Code (OpenCode) 透過 LinkPi 串接 LLM (如 Google Gemini) 時，若遇到第一次對話傳送大量上下文導致超過預設的 15 秒等待上限，就會引發 `TimeoutError`，進而造成 OpenCode 不斷重試並卡住。此技能會教小白如何將 `LinkPi.py` 中的等待上限從 15 秒延長至 60 秒，並重新啟動伺服器。

## 使用時機
當強尼反應「LinkPi 回應很慢」、「出現 TimeoutError」或「VS Code 呼叫 pi-google 卡了 1 分鐘」時。

## 執行步驟
1. 使用 `edit` 工具修改當前目錄下的 `LinkPi.py`。
2. 尋找以下兩段程式碼（分別在 `_stream_prompt` 與 `_consolidate` 函數中）：
   ```python
   await proc.send_command({"type": "prompt", "message": prompt}, timeout=15)
   ```
3. 將其替換為：
   ```python
   await proc.send_command({"type": "prompt", "message": prompt}, timeout=60)
   ```
4. 修改存檔後，找出目前執行中的 LinkPi 行程並砍掉：
   ```bash
   netstat -ano | grep 8765
   # 找出 PID 後
   taskkill //F //PID <PID>
   ```
5. 重新在背景啟動 LinkPi，並綁定至 `0.0.0.0`：
   ```bash
   nohup python LinkPi.py --host 0.0.0.0 > linkpi.log 2>&1 &
   ```
6. 回報強尼設定已更新並重新啟動完成，現在對話不會再因為上下文過長而輕易逾時。
