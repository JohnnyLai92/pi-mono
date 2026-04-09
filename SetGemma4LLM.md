# Gemma 4 31B — MacBook 本地部署安裝文件

> **最後更新**：2026-04-06  
> **適用環境**：macOS + Apple Silicon（M1/M2/M3/M4/M5）  
> **預估時間**：首次安裝約 30 分鐘（含模型下載）  
> **成本**：$0（完全免費、完全離線）

---

## 目錄

1. [硬體需求](#1-硬體需求)
2. [安裝 Homebrew](#2-安裝-homebrew)
3. [安裝 uv](#3-安裝-uv)
4. [安裝 vMLX 推理引擎](#4-安裝-vmlx-推理引擎)
5. [設定 HuggingFace Token](#5-設定-huggingface-token)
6. [啟動模型](#6-啟動模型)
7. [安裝聊天介面](#7-安裝聊天介面)
8. [日常使用（每次開機）](#8-日常使用每次開機)
9. [疑難排解](#9-疑難排解)

---

## 1. 硬體需求

| 項目 | 最低需求 | 建議 |
|------|---------|------|
| 處理器 | Apple Silicon（M1 以上） | M4 Pro / M4 Max |
| 統一記憶體 | 24GB | 48GB+（餘裕更大） |
| 硬碟空間 | 23GB | 30GB+（含快取） |
| macOS | Ventura 13+ | 最新版 |

> **⚠️ 16GB RAM 替代方案**：改跑 26B MoE 版（15GB），指令改為：
> ```bash
> vmlx serve dealignai/Gemma-4-26B-MoE-CRACK --port 8080
> ```

### 記憶體分配參考（48GB 為例）

```
模型載入    ~21GB
系統開銷    ~4GB
可用餘量    ~23GB  ← 足夠同時開其他應用
```

---

## 2. 安裝 Homebrew

> 如果已安裝，可跳過。執行 `brew --version` 確認。

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

安裝完成後，**依照 Terminal 提示**將 Homebrew 加入 PATH：

```bash
# Apple Silicon Mac 預設路徑
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc
```

驗證：

```bash
brew --version
# 預期輸出：Homebrew 5.x.x
```

---

## 3. 安裝 uv

> Python 套件管理工具，比 pip 快 100 倍。

```bash
brew install uv
```

驗證：

```bash
uv --version
# 預期輸出：uv 0.x.x
```

---

## 4. 安裝 vMLX 推理引擎

> 專為 Apple Silicon 設計的 LLM 推理引擎，**必須用 vMLX**（Ollama / mlx_lm 不支援 Gemma 4）。

### 標準安裝

```bash
uv tool install vmlx
```

### ⚠️ 若遇到模型載入錯誤，改裝 GitHub 最新版

```bash
uv tool install \
  "vmlx @ git+https://github.com/jjang-ai/vmlx.git" \
  --force
```

> **實測經驗**：PyPI 版可能遇到 `ValueError: Expected shape` 錯誤，  
> GitHub 版已修復 Gemma 4 架構相容問題，建議直接裝 GitHub 版。

### 設定 PATH

```bash
# 確認 ~/.local/bin 在 PATH 中
echo $PATH | grep -q ".local/bin" || {
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
  source ~/.zshrc
}
```

驗證：

```bash
which vmlx
# 預期輸出：/Users/<你的帳號>/.local/bin/vmlx
```

---

## 5. 設定 HuggingFace Token

### 5.1 建立 Token

1. 開啟 https://huggingface.co/settings/tokens
2. 點擊 **Create new token**
3. 權限選 **Read**
4. 複製產生的 Token（格式：`hf_xxxxxxxx`）

### 5.2 接受 Gemma 授權

1. 開啟 https://huggingface.co/google/gemma-4-31b-it
2. 點擊 **Accept License** 接受使用條款

### 5.3 安裝 HuggingFace CLI 並設定 Token

```bash
# 安裝 CLI
uv tool install huggingface_hub

# 設定 Token 環境變數（替換成你的 Token）
export HF_TOKEN="hf_你的Token"
echo 'export HF_TOKEN="hf_你的Token"' >> ~/.zshrc
source ~/.zshrc
```

驗證：

```bash
hf auth whoami
# 預期輸出：✓ Logged in
#           user: 你的帳號名稱
```

---

## 6. 啟動模型

### 首次啟動（自動下載模型 ~18GB）

```bash
vmlx serve dealignai/Gemma-4-31B-JANG_4M-CRACK --port 8080
```

首次會下載 13 個檔案（5 個 safetensors 分片 + 設定檔），約需 10-20 分鐘，視網路速度而定。

### 啟動成功的標誌

```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8080 (Press CTRL+C to quit)
```

### 快速測試

開另一個 Terminal 視窗：

```bash
curl -s http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local",
    "messages": [{"role": "user", "content": "你好，用一句話介紹你自己"}],
    "max_tokens": 100
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['choices'][0]['message']['content'])"
```

預期輸出：模型的中文自我介紹回應。

---

## 7. 安裝聊天介面

### 方案 A：Open WebUI（推薦）

> ✅ 對話記錄 ✅ 多模型切換 ✅ RAG ✅ 美觀介面

**前置需求**：Docker Desktop for Mac（https://www.docker.com/products/docker-desktop/）

```bash
docker run -d \
  -p 3000:8080 \
  -e OPENAI_API_BASE_URL=http://host.docker.internal:8080/v1 \
  -e OPENAI_API_KEY=none \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main
```

等約 15 秒後開啟：**http://localhost:3000**
- 第一次需建立本地帳號（隨便填，純本地儲存）
- 建完帳號即可開始對話

### 方案 B：Gradio（極簡，3 行程式）

> ✅ 5 分鐘搞定 ❌ 無對話記錄

```bash
# 建虛擬環境
python3 -m venv ~/.venv && source ~/.venv/bin/activate
pip install gradio openai
```

建立 `chat.py`：

```python
import gradio as gr

gr.load_chat(
    "http://localhost:8080/v1/",
    model="local"
).launch()
```

啟動：

```bash
python chat.py
# → 開啟 http://localhost:7860
```

---

## 8. 日常使用（每次開機）

模型已快取在本地（`~/.cache/huggingface/`），之後啟動只需幾秒。

### 每次只需兩個步驟

```bash
# ① 啟動模型（開一個 Terminal 視窗）
vmlx serve dealignai/Gemma-4-31B-JANG_4M-CRACK --port 8080

# ② 開啟瀏覽器
#    Open WebUI → http://localhost:3000  （Docker 通常會自動啟動）
#    Gradio     → python chat.py → http://localhost:7860
```

### 背景啟動模型（可選）

如果不想佔用一個 Terminal 視窗：

```bash
nohup vmlx serve dealignai/Gemma-4-31B-JANG_4M-CRACK --port 8080 \
  > /tmp/vmlx.log 2>&1 &

# 查看 log
tail -f /tmp/vmlx.log

# 停止模型
kill $(pgrep -f "vmlx serve")
```

### 確認 Open WebUI 是否運行中

```bash
docker ps | grep open-webui

# 如果沒有運行，手動啟動：
docker start open-webui
```

---

## 9. 疑難排解

### ❌ `ValueError: Expected shape (8192, 672) but received shape (8192, 1344)`

**原因**：PyPI 版 vMLX 不支援 Gemma 4 架構  
**解法**：改裝 GitHub 最新版

```bash
uv tool install \
  "vmlx @ git+https://github.com/jjang-ai/vmlx.git" \
  --force
```

### ❌ `401 Unauthorized` 或模型下載失敗

**原因**：HuggingFace Token 未設定或未接受 Gemma 授權  
**解法**：

```bash
# 確認 Token
echo $HF_TOKEN

# 重新設定
export HF_TOKEN="hf_你的Token"

# 確認授權：開啟 https://huggingface.co/google/gemma-4-31b-it 點 Accept
```

### ❌ `Cannot connect to the Docker daemon`

**原因**：Docker Desktop 未啟動  
**解法**：從應用程式中開啟 Docker Desktop，等待圖示變綠色

### ❌ 記憶體不足 / 系統卡頓

**原因**：RAM 不夠跑 31B 模型  
**解法**：

```bash
# 停止模型
kill $(pgrep -f "vmlx serve")

# 改跑較小的 MoE 版本（僅需 ~15GB）
vmlx serve dealignai/Gemma-4-26B-MoE-CRACK --port 8080
```

### ❌ Port 8080 或 3000 被佔用

```bash
# 查看佔用的程序
lsof -i :8080
lsof -i :3000

# 改用其他 port
vmlx serve dealignai/Gemma-4-31B-JANG_4M-CRACK --port 8081

# Open WebUI 改 port
docker rm -f open-webui
docker run -d -p 3001:8080 \
  -e OPENAI_API_BASE_URL=http://host.docker.internal:8081/v1 \
  -e OPENAI_API_KEY=none \
  --name open-webui \
  ghcr.io/open-webui/open-webui:main
```

### 清除模型快取（釋放硬碟空間）

```bash
# 查看快取大小
du -sh ~/.cache/huggingface/

# 清除（下次啟動需重新下載）
rm -rf ~/.cache/huggingface/hub/models--dealignai--Gemma-4-31B-JANG_4M-CRACK
```

---

## 附錄：安裝檢查清單

安裝完成後，可逐項確認：

```bash
# 1. Homebrew
brew --version

# 2. uv
uv --version

# 3. vMLX
which vmlx

# 4. HuggingFace 登入
hf auth whoami

# 5. 模型是否可啟動
vmlx serve dealignai/Gemma-4-31B-JANG_4M-CRACK --port 8080

# 6. API 回應測試
curl -s http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"local","messages":[{"role":"user","content":"hello"}],"max_tokens":50}'

# 7. Open WebUI
docker ps | grep open-webui
# → 瀏覽器開啟 http://localhost:3000

# 8. 記憶體使用
memory_pressure
```

---

> 📌 **模型資訊**  
> - 名稱：dealignai/Gemma-4-31B-JANG_4M-CRACK  
> - 基底：Google Gemma 4 31B  
> - 技術：Abliteration（移除拒絕向量，非提示詞越獄）  
> - 大小：~18GB（bf16 safetensors × 5 分片）  
> - 來源：HuggingFace  
> - 授權：需接受 Google Gemma License
