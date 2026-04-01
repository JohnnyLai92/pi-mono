<!-- OSS_WEEKEND_START -->
# 🏖️ OSS 週末

**Issue 追蹤器將於 2026 年 4 月 6 日（週一）重新開放。**

OSS 週末活動從 2026 年 3 月 27 日（週五）持續至 4 月 6 日（週一）。此期間新開的 issue 將自動關閉。如需支援，請加入 [Discord](https://discord.com/invite/3cU7Bz4UPx)。
<!-- OSS_WEEKEND_END -->

---

<p align="center">
  <a href="https://shittycodingagent.ai">
    <img src="https://shittycodingagent.ai/logo.svg" alt="pi logo" width="128">
  </a>
</p>
<p align="center">
  <a href="https://discord.com/invite/3cU7Bz4UPx"><img alt="Discord" src="https://img.shields.io/badge/discord-community-5865F2?style=flat-square&logo=discord&logoColor=white" /></a>
  <a href="https://github.com/badlogic/pi-mono/actions/workflows/ci.yml"><img alt="Build status" src="https://img.shields.io/github/actions/workflow/status/badlogic/pi-mono/ci.yml?style=flat-square&branch=main" /></a>
</p>
<p align="center">
  <a href="https://pi.dev">pi.dev</a> 網域由
  <br /><br />
  <a href="https://exe.dev"><img src="packages/coding-agent/docs/images/exy.png" alt="Exy mascot" width="48" /><br />exe.dev</a> 慷慨贊助
</p>

**語言：** [English](README.md) | **繁體中文**

---

# Pi Monorepo

> **尋找 pi 程式開發代理？** 請參閱 **[packages/coding-agent](packages/coding-agent)** 了解安裝與使用方式。

用於建構 AI 代理和管理 LLM 部署的工具集。

## 套件

| 套件 | 說明 |
|------|------|
| **[@mariozechner/pi-ai](packages/ai)** | 統一的多供應商 LLM API（OpenAI、Anthropic、Google 等） |
| **[@mariozechner/pi-agent-core](packages/agent)** | 支援工具呼叫與狀態管理的代理執行環境 |
| **[@mariozechner/pi-coding-agent](packages/coding-agent)** | 互動式程式開發代理 CLI |
| **[@mariozechner/pi-mom](packages/mom)** | 將訊息委派給 pi 程式開發代理的 Slack 機器人 |
| **[@mariozechner/pi-tui](packages/tui)** | 差分渲染終端 UI 函式庫 |
| **[@mariozechner/pi-web-ui](packages/web-ui)** | AI 聊天介面的 Web 元件 |
| **[@mariozechner/pi-pods](packages/pods)** | 管理 GPU Pod 上 vLLM 部署的 CLI |

## LinkPi – OpenCode（VS Code）橋接器

[`LinkPi.py`](LinkPi.py) 是一個 Python 中介程式，將 pi 代理暴露為 OpenAI 相容的 HTTP API，讓 [OpenCode](https://opencode.ai)（VS Code 擴充功能）能夠使用 pi 作為其程式開發代理後端。

每個 LLM 供應商擁有獨立的 pi session 和 session 目錄。在 OpenCode 模型選擇器中切換供應商時，LinkPi 會自動壓縮舊 session、萃取交接摘要，並注入至新 session 的上下文中。`/v1/consolidate` 端點可讓 pi 本身將所有供應商摘要彙整為單一統一記憶文件。

### 架構

```
OpenCode (VS Code)
  POST /v1/chat/completions
  model: "link-pi/<provider>"   ← 供應商名稱編碼於模型名稱中
          │
          ▼
  LinkPi.py  (FastAPI，埠號 8765)
    │
    ├── ProviderRegistry
    │     每個供應商對應一個 PiProcess，各有獨立 session 目錄
    │     偵測供應商切換 → 壓縮舊 session → 更新 SharedMemory
    │
    ├── SharedMemory  (~/.linkpi/memory.md)
    │     跨供應商上下文，每個新 session 啟動時自動注入
    │
    └── /v1/consolidate
          啟動一個臨時 pi session，餵入所有摘要，
          請其產出單一統一記憶文件
    │
    │  JSONL over stdin/stdout  (pi RPC 協定)
    ▼
  pi --mode rpc  (每個供應商一個子行程)
    │  --session-dir ~/.linkpi/sessions/<provider>/
    ▼
  LLM 供應商  (Anthropic / OpenAI / Google / …)
```

### 記憶體流程

```
使用者在 OpenCode 模型選擇器中從 Anthropic 切換至 OpenAI
  1. LinkPi 壓縮 Anthropic 的 pi session
  2. Pi 回傳交接摘要（純文字）
  3. 摘要附加至 ~/.linkpi/memory.md
  4. OpenAI pi session 啟動，共享記憶體作為 [Context] 區塊
     預先置入第一條使用者訊息
  5. OpenAI 能完整了解 Anthropic 所做的工作並繼續進行

POST /v1/consolidate
  啟動一個臨時 pi session，餵入所有供應商摘要，
  請其彙整為單一統一記憶文件 → 取代 memory.md
```

### 安裝設定

#### 1. 安裝 Python 依賴套件

```bash
pip install fastapi uvicorn
```

#### 2. 準備 pi 執行檔

**若 pi 已全域安裝**（`npm install -g @mariozechner/pi-coding-agent`）：

```bash
# Linux/macOS
python LinkPi.py

# Windows — npm 全域腳本為 .cmd 包裝器
python LinkPi.py --pi-cmd pi.cmd
```

**若從原始碼執行（本 monorepo）：**

Linux/macOS — 使用 `pi-test.sh`：
```bash
python LinkPi.py --pi-cmd ./pi-test.sh
```

Windows — 在 repo 根目錄建立 `pi.cmd`：
```batch
@echo off
node "%~dp0node_modules\tsx\dist\cli.mjs" "%~dp0packages\coding-agent\src\cli.ts" %*
```
然後啟動 LinkPi：
```cmd
python LinkPi.py --pi-cmd pi.cmd
```

> **Windows `node_modules` 注意事項：** 若 `node_modules` 是在 WSL/Linux 環境下安裝的，原生二進位檔（esbuild 等）僅支援 Linux。修復方式：在 Windows 終端機執行 `npm install` 以重新安裝平台專屬套件。若 `.bin/` 發生權限錯誤，請先從 WSL 刪除（`rm -rf node_modules/.bin`），再從 Windows 執行 `npm install`。

#### 3. 設定本地 LLM 供應商（選用）

若要新增自架模型（Ollama、vLLM、LM Studio），請建立 `~/.pi/agent/models.json`：

- **Windows：** `C:\Users\<使用者名稱>\.pi\agent\models.json`
- **Linux/macOS：** `~/.pi/agent/models.json`

首先確認伺服器提供哪些模型：
```bash
curl http://<你的伺服器>/v1/models
```

以執行 Qwen3-Coder 的 vLLM 伺服器為例：
```json
{
  "providers": {
    "local-llm": {
      "baseUrl": "http://192.168.249.11:8060/v1",
      "api": "openai-completions",
      "apiKey": "local",
      "compat": {
        "supportsDeveloperRole": false,
        "supportsReasoningEffort": false,
        "supportsUsageInStreaming": false,
        "maxTokensField": "max_tokens",
        "thinkingFormat": "qwen-chat-template"
      },
      "models": [
        {
          "id": "qwen3-coder",
          "name": "Qwen3-Coder 30B（本地）",
          "reasoning": true,
          "input": ["text"],
          "contextWindow": 100000,
          "maxTokens": 16384,
          "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
        }
      ]
    }
  }
}
```

驗證 pi 能看到該模型（開啟 `/model` 時自動重新載入，無需重啟）：
```bash
pi --list-models local-llm
# provider   model        context  max-out  thinking  images
# local-llm  qwen3-coder  100K     16.4K    yes       no
```

LinkPi 中的 `pi-local` 模型路由至此 `local-llm` 供應商。若需更改供應商名稱，請更新 `LinkPi.py` 中的 `MODEL_TO_PROVIDER`。

#### 4. 設定 opencode.json

將 `opencode.json` 放置於專案目錄旁（或 `~/.config/opencode/config.json` 作為全域設定）：

```json
{
  "$schema": "https://opencode.ai/config.schema.json",
  "model": "link-pi/pi-local",
  "provider": {
    "link-pi": {
      "options": {
        "baseURL": "http://127.0.0.1:8765/v1",
        "apiKey":  "local"
      },
      "models": {
        "pi-anthropic": { "name": "Pi → Anthropic" },
        "pi-openai":    { "name": "Pi → OpenAI" },
        "pi-google":    { "name": "Pi → Google" },
        "pi-groq":      { "name": "Pi → Groq" },
        "pi-mistral":   { "name": "Pi → Mistral" },
        "pi-bedrock":   { "name": "Pi → Bedrock" },
        "pi-vertex":    { "name": "Pi → Vertex" },
        "pi-openrouter":{ "name": "Pi → OpenRouter" },
        "pi-local":     { "name": "Pi → 本地（vLLM/Ollama）" },
        "pi-agent":     { "name": "Pi（預設）" }
      }
    }
  }
}
```

LinkPi 啟動時會印出設定片段。透過 OpenCode 模型選擇器（`Ctrl+M`）切換供應商。

#### 5. 驗證設定

```bash
# 1. LinkPi 正在執行
curl http://127.0.0.1:8765/v1/models

# 2. Pi 子行程能夠啟動
curl http://127.0.0.1:8765/v1/memory

# 3. 端對端：LinkPi → pi → LLM
curl -s http://127.0.0.1:8765/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"pi-local","stream":false,"messages":[{"role":"user","content":"reply with just PONG"}]}'
```

> **為何使用 `options.baseURL` 而非頂層 `baseURL`？**
> OpenCode 的供應商 schema 使用 `.strict()`——頂層僅允許 `name`、`npm`、`models`、`options`、`whitelist`、`blacklist`。`baseURL` 和 `apiKey` 必須巢狀於 `options` 內，否則會出現 `Unrecognized keys` 驗證錯誤。

### 可用模型

在 `opencode.json` 中修改 `model`，或使用 OpenCode 模型選擇器（`Ctrl+M`）切換供應商。

| 模型（`link-pi/<id>`） | Pi 使用的供應商 |
|------------------------|----------------|
| `pi-anthropic` | `--provider anthropic` |
| `pi-openai` | `--provider openai` |
| `pi-google` | `--provider google` |
| `pi-groq` | `--provider groq` |
| `pi-mistral` | `--provider mistral` |
| `pi-bedrock` | `--provider bedrock` |
| `pi-vertex` | `--provider vertex` |
| `pi-openrouter` | `--provider openrouter` |
| `pi-local` | `local-llm`（透過 `~/.pi/agent/models.json`） |
| `pi-agent` | pi 自動選擇供應商 |

### CLI 選項

| 選項 | 預設值 | 說明 |
|------|--------|------|
| `--host` | `127.0.0.1` | 綁定位址 |
| `--port` | `8765` | 埠號 |
| `--pi-cmd` | `pi` | pi 執行檔路徑 |
| `--model` | *（pi 預設）* | pi 內部的預設模型，例如 `anthropic/claude-sonnet-4` |
| `--thinking` | *（pi 預設）* | 思考等級：`off` `minimal` `low` `medium` `high` `xhigh` |

### 端點

| 端點 | 說明 |
|------|------|
| `GET /v1/models` | 列出所有 `link-pi/<provider>` 模型 |
| `POST /v1/chat/completions` | OpenAI 相容的串流聊天 |
| `POST /v1/consolidate` | 請 pi 將所有供應商摘要彙整為統一記憶 |
| `GET /v1/memory` | 查看當前共享記憶體及快照數量 |

### 運作原理

- **每個供應商一個 pi 子行程。** 每個 `link-pi/<provider>` 模型對應一個長駐的 `pi --mode rpc` 行程，各有獨立的 `--session-dir ~/.linkpi/sessions/<provider>/`。Pi 的完整 session 持久化功能（分支、壓縮、`/tree`）在各供應商內正常運作。
- **供應商切換 = 記憶體交接。** 當 OpenCode 切換至不同模型時，LinkPi 壓縮舊 session（使用 pi 的 `compact` RPC 命令搭配交接最佳化指令），萃取摘要並附加至 `~/.linkpi/memory.md`。
- **共享記憶體注入。** 每個新 session 啟動時，`memory.md` 的完整內容會作為 `[Shared memory from previous sessions]` 區塊預先置入第一條使用者訊息，讓新供應商完整了解先前的工作。
- **隨需彙整。** `POST /v1/consolidate` 啟動一個臨時 pi session，餵入所有累積的供應商摘要，請 pi 彙整為單一連貫的記憶文件，取代 `memory.md`。
- **透過 Future 路由回應。** Pi RPC 命令回應（例如 prompt ack、compact 結果）透過以 id 為鍵的 `asyncio.Future` 物件路由，與串流事件佇列分開，讓 `compact` 在供應商切換時能同步執行而不干擾串流。
- **工具執行可見。** Pi 自主呼叫的 `bash`、`read`、`edit` 等工具，以斜體標註串流至 OpenCode，讓使用者能即時追蹤進度。
- **認證由 pi 管理。** API 金鑰和 OAuth Token 由 pi 本身管理（`~/.pi/agent/auth.json` 或環境變數）。OpenCode 設定中的 `apiKey: "local"` 僅為佔位符。

### 已知限制

| 限制 | 說明 |
|------|------|
| 壓縮需要足夠的上下文 | Pi 的 compact 命令需要足夠的對話歷史；過短的 session 無法產出摘要。 |
| 供應商切換會阻塞下一個請求 | 切換後的第一個請求需等待舊 session 壓縮完成才繼續。 |
| 工具呼叫對 OpenCode 不透明 | OpenCode 看到的是純文字，而非結構化的 `tool_call`/`tool_result` 區塊。 |
| 每個供應商同時只能處理一個請求 | 同一供應商的並發請求透過 `asyncio.Lock` 序列化。 |
| Windows 子行程 | 需要 pi 在 `PATH` 中，或透過 `--pi-cmd` 指定路徑。 |

## 貢獻

請參閱 [CONTRIBUTING.md](CONTRIBUTING.md) 了解貢獻指南，以及 [AGENTS.md](AGENTS.md) 了解專案特定規則（適用於人類和 AI 代理）。

## 開發

```bash
npm install          # 安裝所有依賴套件
npm run build        # 建構所有套件
npm run check        # 程式碼檢查、格式化與型別檢查
./test.sh            # 執行測試（未設定 API 金鑰時略過 LLM 相依測試）
./pi-test.sh         # 從原始碼執行 pi（可從任意目錄執行）
```

> **注意：** `npm run check` 需先執行 `npm run build`。web-ui 套件使用 `tsc`，需要依賴項目編譯後的 `.d.ts` 檔案。

## 授權

MIT
