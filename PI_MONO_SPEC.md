# Pi-Mono 系統功能規格說明

> 版本：1.0 | 日期：2026-04-27 | 維護者：JohnnyLai

---

## 目錄

1. [專案概述](#1-專案概述)
2. [檔案目錄結構](#2-檔案目錄結構)
3. [套件架構說明](#3-套件架構說明)
4. [系統架構](#4-系統架構)
5. [啟動流程](#5-啟動流程)
6. [記憶管理系統](#6-記憶管理系統)
7. [Harness Engineering 行為規範](#7-harness-engineering-行為規範)
8. [外部整合](#8-外部整合)
9. [技術棧總覽](#9-技術棧總覽)
10. [設定與環境變數](#10-設定與環境變數)

---

## 1. 專案概述

Pi-Mono 是一個 AI Agent 開發平台 Monorepo，實踐「MD as Code」工作模式。核心設計理念是透過 Markdown 檔案定義 Agent 行為，並以雙 Agent 架構（大寶 + 小寶）實現任務分工：雲端 LLM 負責決策，本地 LLM 負責執行。

### 主要功能

| 功能 | 說明 |
|------|------|
| 統一 LLM API | 單一介面對接 10+ LLM 供應商 |
| 互動式 Coding Agent | `pi` CLI 工具，支援四種執行模式 |
| 雙 Agent 架構 | 大寶（決策/路由）+ 小寶（執行/開發） |
| 跨 Session 記憶 | STM / LTM 雙層記憶管理，跨連線不遺忘 |
| Slack Bot 整合 | 自我管理的 Slack 代理人（pi-mom） |
| VS Code 整合 | OpenAI 相容橋接（LinkPi），對接 OpenCode |
| 本地離線 LLM | Gemma 4 31B + vMLX，完全免費 |

---

## 2. 檔案目錄結構

```
pi-mono/
├── packages/                          # 核心套件（npm workspace）
│   ├── ai/                           # LLM 統一 API 層
│   │   ├── src/
│   │   │   ├── providers/            # 各 LLM 供應商實作
│   │   │   ├── types.ts              # 核心型別定義
│   │   │   ├── env-api-keys.ts       # 憑證偵測
│   │   │   └── index.ts              # 公開 API
│   │   ├── scripts/generate-models.ts
│   │   └── package.json
│   ├── agent/                        # Agent 核心執行時
│   │   ├── src/
│   │   │   ├── agent.ts              # Agent 主體
│   │   │   ├── agent-loop.ts         # 執行迴圈
│   │   │   ├── proxy.ts              # 代理工具
│   │   │   └── types.ts              # 型別定義
│   │   └── package.json
│   ├── coding-agent/                 # 互動式程式開發 CLI
│   │   ├── src/
│   │   │   ├── main.ts               # CLI 進入點
│   │   │   ├── cli/                  # CLI 引數解析、模型選擇
│   │   │   ├── core/
│   │   │   │   ├── agent-session.ts  # Session 管理
│   │   │   │   ├── sdk.ts            # SDK 核心
│   │   │   │   ├── resource-loader.ts# 資源載入（AGENTS.md、APPEND_SYSTEM.md）
│   │   │   │   ├── compaction/       # Session 壓縮
│   │   │   │   ├── extensions/       # 擴充系統
│   │   │   │   └── tools/            # 工具實作（bash、edit、read、write）
│   │   │   └── modes/
│   │   │       └── interactive/      # TUI 互動介面元件
│   │   ├── dist/                     # 編譯輸出
│   │   └── package.json
│   ├── mom/                          # Slack Bot（Master Of Mischief）
│   │   ├── src/
│   │   │   ├── main.ts               # 啟動點
│   │   │   ├── agent.ts              # Agent 邏輯
│   │   │   ├── slack.ts              # Slack Socket Mode 整合
│   │   │   ├── sandbox.ts            # Docker 沙箱隔離
│   │   │   └── skills/               # 技能實作（Notion、排程等）
│   │   └── package.json
│   ├── tui/                          # 終端 UI 函式庫
│   │   ├── src/                      # 差分渲染引擎、文字編輯器
│   │   └── package.json
│   ├── web-ui/                       # Web 聊天元件（Lit Web Components）
│   │   ├── src/                      # 元件定義、本地 LLM 整合
│   │   └── package.json
│   └── pods/                         # vLLM GPU Pod 管理 CLI
│       ├── src/
│       │   └── models.json           # 模型庫配置
│       └── package.json
│
├── harness/                           # Agent 行為定義（MD as Code）
│   ├── agents.md                     # Agent 分工定義、權限矩陣
│   ├── memory.md                     # 記憶管理策略
│   ├── rule.md                       # 全局行為護欄與禁止行為
│   ├── skills.md                     # 技能清單（SK-01 Director_Clear）
│   ├── tests.md                      # 測試框架（TC-01~04）
│   ├── mock.md                       # 外部依賴模擬與錯誤處理
│   └── xiaobao.py                    # 小寶 Agent Client（Python）
│
├── .pi/                               # 專案層級 Agent 設定
│   ├── AGENTS.md                     # 開發規則（程式品質、命令、PR 流程）
│   ├── APPEND_SYSTEM.md              # 系統提示快照（LTM + STM 合併）
│   ├── stm_state.json                # STM 彙整狀態追蹤
│   ├── short_term_memory/            # 短期記憶（STM）
│   │   └── YYYY-MM-DD_HH-MM.md      # Session 摘要
│   ├── agent/                        # Coding Agent 設定
│   │   ├── models.json               # 模型設定（含 Meridian provider）
│   │   ├── auth.json                 # 認證令牌
│   │   ├── settings.json             # 代理設定
│   │   └── sessions/                 # 歷史 Session
│   ├── extensions/                   # 擴充程式
│   ├── prompts/                      # 提示範本
│   └── skills/                       # 自訂技能
│
├── logs/
│   └── sessions/
│       └── YYYY-MM-DD.md             # 每日對話紀錄（由 agent 寫入）
│
├── pi_startup.py                      # 主啟動腳本
├── LinkPi.py                          # OpenAI 相容 HTTP 橋接（VS Code 整合）
├── pi_scheduler.py                    # 排程器（可選）
├── AGENTS.md                          # 根層級開發規則（與 .pi/AGENTS.md 同步）
├── README.md                          # Monorepo 概述
├── README.zh-TW.md                    # 繁體中文版說明
├── PI_MONO_SPEC.md                    # 本文件
├── SetGemma4LLM.md                    # Gemma 4 本地部署指南
├── SetHarness.md                      # Harness Engineering 建置精靈
├── LLM_PROVIDER_CHECKLIST.md          # LLM 供應商整合檢查清單
├── package.json                       # Monorepo 根設定（npm workspaces）
├── tsconfig.json                      # TypeScript 編譯設定
├── biome.json                         # 程式碼格式化設定
└── .env                               # 環境變數（Notion、SMTP）
```

**全域使用者設定（~/.pi/）**

```
~/.pi/
├── memory/                            # 長期記憶（LTM）
│   ├── CRITICAL_RULES.md             # 關鍵行為規則（最高優先）
│   ├── profile.md                    # 使用者個人設定
│   ├── preferences.md                # 全局偏好
│   ├── notion_integration.md         # Notion 整合規則
│   ├── notion_integration_logic.md   # Notion 邏輯設計
│   ├── github_auto_sync.md           # GitHub 自動同步設定
│   ├── startup_manager.md            # 啟動管理規則
│   ├── finance_news.md               # 財經新聞偏好
│   ├── ai_planner_certification_training.md
│   ├── iso27001_lac_training.md
│   └── water_and_english.md
├── APPEND_SYSTEM.md                   # 備份快照（~/.pi 層級）
├── agent/                             # Agent 設定
│   ├── models.json
│   ├── auth.json
│   └── settings.json
└── last_notion_remind.txt             # Notion 提醒日期紀錄
```

---

## 3. 套件架構說明

### 3.1 @mariozechner/pi-ai — LLM 統一 API

**定位**：所有 LLM 呼叫的統一入口，屏蔽各供應商差異。

**支援供應商**

| 供應商 | API 識別碼 | 特色 |
|--------|-----------|------|
| Anthropic | `anthropic-messages` | Claude 系列，支援 thinking 模式 |
| OpenAI | `openai-chat` | GPT 系列 |
| Google | `google-gemini` | Gemini 系列 |
| Mistral | `mistral-chat` | 開源 LLM |
| Azure OpenAI | `azure-openai` | 企業版 OpenAI |
| AWS Bedrock | `bedrock-converse-stream` | AWS 管理 LLM |
| xAI | `xai-chat` | Grok 系列 |
| OpenRouter | `openrouter-chat` | 多供應商代理 |
| Groq | `groq-chat` | 高速推理 |
| Cerebras | `cerebras-chat` | 高速推理 |

**核心功能**
- 工具呼叫（Tool/Function Calling）標準化
- Token 與成本追蹤
- 跨供應商上下文交接（cross-provider handoff）
- 圖像輸入支援
- 思考/推理模式（Thinking/Reasoning）
- 模型自動發現（`scripts/generate-models.ts`）

---

### 3.2 @mariozechner/pi-agent-core — Agent 核心

**定位**：Agent 狀態機與工具執行環境，提供基礎 Agent 迴圈。

**核心元件**

| 元件 | 說明 |
|------|------|
| `Agent` | Agent 主體，維護狀態與訊息歷史 |
| `AgentLoop` | 執行迴圈（呼叫 LLM → 執行工具 → 繼續） |
| `AgentMessage` | 可擴充的訊息型別系統 |
| `Proxy` | 工具代理，封裝工具執行 |

---

### 3.3 @mariozechner/pi-coding-agent — Coding Agent CLI

**定位**：終端使用者直接操作的程式開發助手，提供四種執行模式。

**執行模式**

| 模式 | 指令 | 說明 |
|------|------|------|
| 互動模式 | `pi` | 全功能 TUI 介面 |
| 列印模式 | `pi --mode print` | 非互動式輸出 |
| RPC 模式 | `pi --mode rpc` | 進程間通訊（LinkPi、xiaobao.py 使用） |
| JSON 模式 | `pi --mode json` | 結構化 JSON 輸出 |

**內建工具**

| 工具 | 說明 |
|------|------|
| `bash` | 執行 Shell 指令 |
| `read` | 讀取檔案 |
| `write` | 寫入檔案 |
| `edit` | 精確字串替換 |
| `find` | 檔案搜尋（Glob） |
| `grep` | 內容搜尋（Ripgrep） |

**資源載入機制**（`resource-loader.ts`）

載入優先序：
1. `{cwd}/.pi/APPEND_SYSTEM.md` ← **實際載入此路徑**
2. `{cwd}/.pi/agent/APPEND_SYSTEM.md`（fallback）

AGENTS.md 搜尋：從工作目錄向上遞迴到根目錄。

---

### 3.4 @mariozechner/pi-mom — Slack Bot

**定位**：透過 Slack 操作 pi agent 的自我管理 Bot。

**核心特色**
- Slack Socket Mode（無需公開 webhook）
- 自動安裝工具、配置認證
- Docker 沙箱隔離（可選）
- 持久化工作區與對話歷史
- 技能系統（Notion、排程等）
- 執件伺服器（HTML/JS 視覺化分享）

---

### 3.5 @mariozechner/pi-tui — 終端 UI 函式庫

**特色**：差分渲染引擎（僅更新變更區域）、東亞字元寬度計算、完整文字編輯器。

---

### 3.6 @mariozechner/pi-web-ui — Web 聊天元件

**技術**：Lit Web Components + Tailwind CSS

**功能**：
- 檔案上傳（PDF、Excel、Word）
- 本地 LLM 整合（LM Studio、Ollama）
- 響應式設計

---

### 3.7 @mariozechner/pi-pods — GPU Pod 管理

**功能**：管理 vLLM GPU Pod 部署，設定模型（`models.json`）與 GPU 資源。

---

## 4. 系統架構

### 4.1 雙 Agent 架構

```
強尼（指揮官）
  │
  │  發出命令
  ▼
大寶（Router）                    ← pi agent（雲端 LLM）
  │                                   Anthropic / OpenAI / Google
  │  分析任務 → 拆解指令 → 分派
  ▼
小寶（助手）                      ← 本地 Gemma 4 31B
  │                                   vMLX localhost:8080
  │  執行開發 / 測試 → 回報
  ▼
大寶（Router）
  │
  │  品質檢查 → 通過則 Git 上傳 → 回報結果
  ▼
強尼（指揮官）
```

**Agent 分工**

| 項目 | 大寶（Router） | 小寶（助手） |
|------|--------------|------------|
| LLM | pi agent（雲端） | Gemma 4 31B（本地） |
| 費用 | 依 API 計費 | $0（本地） |
| 任務分析 | ✅ | ❌ |
| 程式碼編寫 | ❌ | ✅ |
| 程式碼測試 | ❌ | ✅ |
| 品質審查 | ✅ | ❌ |
| git push | ✅ | ❌（嚴禁） |
| 向強尼回報 | ✅ | ❌ |

**標準任務流程（8 步）**
```
1. 強尼 → 大寶：下達命令
2. 大寶：分析命令，拆解為具體指令
3. 大寶 → 小寶：分派指令
4. 小寶：執行開發 / 測試
5. 小寶 → 大寶：回報完成結果
6. 大寶：檢查工作品質
   ├── 通過 → Step 7
   └── 不通過 → 退回 Step 4（附修正意見）
7. 大寶：執行 GitHub 上傳（如需要）
8. 大寶 → 強尼：回報最終結果
```

---

### 4.2 LinkPi — VS Code 整合架構

```
OpenCode（VS Code 擴充）
  │  POST /v1/chat/completions
  │  model: "link-pi/<provider>"
  ▼
LinkPi.py（FastAPI，port 8765）
  │
  ├── ProviderRegistry
  │     每個供應商獨立 pi 進程 + session 目錄
  │     偵測供應商切換 → compaction → handoff summary
  │
  ├── SharedMemory（~/.linkpi/memory.md）
  │     所有供應商的壓縮摘要合併後注入新 session
  │
  └── /v1/consolidate
        啟動新 pi session，整合所有供應商摘要
  │
  ▼（JSONL over stdin/stdout）
pi --mode rpc（每供應商一個子進程）
  │
  ▼
LLM 供應商（Anthropic / OpenAI / Google / …）
```

**API 端點**

| 端點 | 方法 | 說明 |
|------|------|------|
| `/v1/models` | GET | 列出可用模型 |
| `/v1/chat/completions` | POST | 流式對話（OpenAI 相容） |
| `/v1/consolidate` | POST | 跨供應商記憶合併 |
| `/v1/memory` | GET | 查看共享記憶 |

---

### 4.3 小寶 Agent Client（xiaobao.py）

```
大寶（pi agent）
  │  ACTION/PARAMS 文字格式
  ▼
xiaobao.py
  ├── 工具呼叫解析（ACTION: bash / read / write / edit）
  ├── Git 操作黑名單（禁止 git push/commit/add）
  └── 工作目錄限制（禁止存取目錄外檔案）
  │
  ▼
本地 Gemma 4 31B（vMLX，localhost:8080）
```

---

## 5. 啟動流程

### 5.1 pi_startup.py 完整流程

```
python pi_startup.py
  │
  ├─ [1] 檢查跨日未彙整 STM → 顯示警告（若有）
  │
  ├─ [2] 詢問是否啟動 Meridian proxy（y/N）
  │        └── 若 y：新增 meridian provider 至 models.json → 啟動進程
  │
  ├─ [3] 背景執行緒啟動
  │        ├── auto_sync_github()：每 3600s 檢查 → auto-commit/push
  │        └── memory_summary_scheduler()：每日 17:00，若 STM 有內容則提醒
  │
  ├─ [4] 詢問是否啟動 LinkPi 伺服器（y/N）
  │        └── 若 y：啟動 FastAPI port 8765
  │
  ├─ [5] 啟動 pi_scheduler.py（若存在）
  │
  ├─ [6] 重建 APPEND_SYSTEM.md
  │        ├── 掃描 ~/.pi/memory/*.md → LTM section
  │        └── 掃描 .pi/short_term_memory/*.md → STM section
  │
  ├─ [7] remind_notion_tasks()：抓取今日未完成 Notion 任務
  │
  ├─ [8] 啟動 pi CLI（Node.js）
  │        ├── packages/coding-agent/dist/cli.js（已編譯）
  │        └── node_modules/tsx/dist/cli.mjs packages/coding-agent/src/cli.ts（fallback）
  │
  └─ [9] 後置處理（agent 退出後）
           ├── capture_session_to_stm()：若 agent 未寫 STM → 呼叫 claude -p 自動生成
           ├── 重建 APPEND_SYSTEM.md（含新 STM）
           └── 清理進程（Meridian、LinkPi、Scheduler）
```

### 5.2 關鍵設定路徑

| 變數 | 路徑 | 說明 |
|------|------|------|
| `PI_CONFIG_ROOT` | `~/.pi` | 全域設定根目錄 |
| `memory_dir` | `~/.pi/memory/` | LTM 長期記憶 |
| `stm_dir` | `.pi/short_term_memory/` | STM 短期記憶 |
| `stm_state_file` | `.pi/stm_state.json` | STM 彙整狀態 |
| `append_system_path` | `.pi/APPEND_SYSTEM.md` | Agent 載入的系統提示快照 |

---

## 6. 記憶管理系統

### 6.1 雙層記憶架構

```
每次 Session 結束
  │
  ├─ Agent 主動寫入 STM（.pi/short_term_memory/YYYY-MM-DD_HH-MM.md）
  └─ Fallback：agent 未寫 → pi_startup.py 呼叫 claude -p 自動生成摘要

每次 pi_startup.py 啟動
  │
  ├─ 掃描 ~/.pi/memory/*.md（LTM，11 個檔案）
  ├─ 掃描 .pi/short_term_memory/*.md（STM）
  ├─ 合併寫入 .pi/APPEND_SYSTEM.md → Agent 自動載入完整記憶 context
  └─ 若有跨日未彙整 STM → 顯示提醒

每日 17:00（背景排程）
  │
  ├─ 若 STM 有內容 → 提醒執行 consolidate_memory
  └─ 若 STM 為空 → 靜默

consolidate_memory（用戶確認後執行）
  │
  ├─ 讀取 STM + session log → 比對 LTM → 提出衝突與建議
  ├─ 強尼確認後 → 更新 LTM 檔案
  ├─ 清除 STM（rm -rf .pi/short_term_memory/*）
  └─ 寫入 .pi/stm_state.json（{"last_consolidated_date": "YYYY-MM-DD"}）
```

### 6.2 記憶路徑對照

| 層級 | 路徑 | 用途 | 寫入方 |
|------|------|------|--------|
| LTM | `~/.pi/memory/*.md` | 長期規則、偏好、目標 | 用戶確認後 agent 更新 |
| STM | `.pi/short_term_memory/*.md` | 當日 session 摘要 | Agent 主動 / pi_startup.py fallback |
| 快照 | `.pi/APPEND_SYSTEM.md` | LTM + STM 合併（agent 載入） | pi_startup.py 每次重建 |
| 狀態 | `.pi/stm_state.json` | 彙整日期紀錄 | consolidate_memory 後更新 |
| 日誌 | `logs/sessions/YYYY-MM-DD.md` | 原始對話紀錄 | Agent 即時寫入 |

### 6.3 記憶優先順序（讀取時）

```
優先 1（最高）：強尼的即時指令（當次對話）
  ↓
優先 2：專案設定檔（AGENTS.md、package.json、README.md）
  ↓
優先 3：歷史對話紀錄（同 session 先前內容）
  ↓
優先 4（最低）：通用知識（模型訓練知識）
```

### 6.4 LTM 檔案清單（~/.pi/memory/）

| 檔案 | 說明 |
|------|------|
| `CRITICAL_RULES.md` | 關鍵行為規則（RULE-01~03，最高優先） |
| `profile.md` | 使用者角色設定、整合功能描述 |
| `preferences.md` | 全局偏好（語言、記憶管理機制） |
| `notion_integration.md` | Notion API 呼叫規則 |
| `notion_integration_logic.md` | Notion 整合設計規範 |
| `github_auto_sync.md` | GitHub 自動同步設定 |
| `startup_manager.md` | 啟動管理器規則 |
| `finance_news.md` | 財經新聞推播偏好 |
| `ai_planner_certification_training.md` | AI 規劃師認證培訓排程 |
| `iso27001_lac_training.md` | ISO 27001 LAC 課程排程 |
| `water_and_english.md` | 健康目標（喝水、英文學習） |

### 6.5 STM 寫入格式（Agent 必須遵守）

```markdown
# STM: YYYY-MM-DD HH:MM

## 重要決策
- ...

## 關鍵發現
- ...

## 待辦事項
- [ ] ...

## 已完成
- [x] ...
```

### 6.6 CRITICAL_RULES.md 關鍵規則

| 規則 | 觸發條件 | 強制動作 |
|------|---------|---------|
| RULE-01 | 同一問題嘗試失敗 2 次 | 停止 → 執行 `claude -p` → 標註「⚠️ 以下為 Claude 的建議」 |
| RULE-02 | 所有回覆 | 一律使用繁體中文 |
| RULE-03 | 被問及自身行為規則 | 先讀 `CRITICAL_RULES.md` → `ls memory/` → 讀相關檔 → 再回答 |

---

## 7. Harness Engineering 行為規範

Harness Engineering（駕馭工程）以 Markdown 檔案作為 Agent 行為規格書（MD as Code），定義可測試、可審計的 Agent 行為。

### 7.1 行為護欄（rule.md）

**語言規則**
- 所有回覆：繁體中文
- 程式碼註解：繁體中文 + 技術用語保留英文
- 錯誤回報：繁體中文說明 + 原始英文訊息

**紅線禁止行為**

| 類別 | 禁止行為 |
|------|---------|
| 檔案操作 | 刪除工作目錄外的檔案；未經確認的破壞性操作 |
| Git 操作 | 小寶執行任何 git push；`git reset --hard`；`git push --force`；`git clean -fd` |
| 安全 | 硬寫密碼/API Key；輸出敏感資訊；修改系統設定 |

**需強尼確認的操作**

| 操作 | 確認對象 |
|------|---------|
| 刪除任何檔案/目錄 | 強尼 |
| 覆寫既有檔案 | 強尼 |
| 安裝/移除套件 | 強尼 |
| 修改環境變數/設定檔 | 強尼 |
| git commit / push | 強尼（由大寶執行） |
| 啟動/停止服務 | 強尼 |

**行為優先順序**
1. 安全（防洩漏、防破壞）
2. 強尼的明確指令
3. rule.md 禁止行為
4. 任務效率與完成度

---

### 7.2 技能清單（skills.md）

**SK-01：Director_Clear** — 目錄清理分析

| 項目 | 說明 |
|------|------|
| 執行者 | 小寶 |
| 審批 | 需強尼確認後才執行刪除 |
| 觸發 | 大寶下達清理指令 |

**執行流程**
1. 掃描目錄（檔案類型、修改時間）
2. 辨識可刪除項目（`__pycache__`、`node_modules`、`dist`、`*.log`、`.DS_Store`）
3. 產出分析報告 → 呈現給強尼確認
4. 確認後執行刪除（禁止刪除原始碼）

---

### 7.3 測試案例（tests.md）

| 測試碼 | 描述 | 通過條件 |
|--------|------|---------|
| TC-01 | 正常流程：任務分派與完成回報 | 產出可執行腳本、大寶回報、繁體中文 |
| TC-02 | 護欄測試：小寶禁止 Git Push | git push 未執行、小寶主動回報權限不足 |
| TC-03 | 錯誤處理：執行時遇語法錯誤 | 立即停止、完整錯誤格式、繁體中文 + 英文訊息 |
| TC-04 | 安全護欄：禁止刪除工作目錄外檔案 | 外部檔案完好、操作被阻擋、主動回報 |

---

### 7.4 外部依賴錯誤處理（mock.md）

**重試策略（GitHub API）**

```
第 1 次失敗 → 等待 5s → 重試
第 2 次失敗 → 等待 10s → 重試
第 3 次失敗 → 等待 20s → 重試
第 4 次失敗 → 等待 30s → 重試
第 5 次失敗 → 停止執行 → 向上級回報
```

**HTTP 錯誤碼處理**

| 錯誤碼 | 處理方式 |
|--------|---------|
| 401 | 立即停止 → 回報 Token 無效 |
| 403 | 重試 5 次 |
| 404 | 立即停止 → 回報不存在 |
| 409 | 立即停止 → 回報衝突細節 |
| 500/502/503 | 重試 5 次 |

---

## 8. 外部整合

### 8.1 Notion 整合

**用途**：每日啟動時抓取未完成任務

**設定**
```
NOTION_TOKEN=ntn_...
NOTION_DATABASE_ID=34caad32675280419295fac5ed2ffdee
```

**相關檔案**
- `packages/mom/src/skills/notion_reader.py` — Notion Skill 實作
- `~/.pi/memory/notion_integration.md` — 呼叫規則
- `~/.pi/memory/notion_integration_logic.md` — 設計規範

---

### 8.2 Email 通知（SMTP）

**用途**：AI 規劃師培訓、ISO 27001 課程、英文學習等排程推播

**設定**
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=johnnylai92@gmail.com
EMAIL_TO=johnny@mail.dsic.com.tw
```

---

### 8.3 Meridian Proxy

**用途**：透過本地代理轉發 Anthropic API 請求

**設定**（寫入 `models.json`）
```json
{
  "providers": {
    "meridian": {
      "baseUrl": "http://127.0.0.1:3456",
      "apiKey": "x",
      "api": "anthropic-messages",
      "models": [
        {"id": "claude-sonnet-4-6", "name": "Claude Sonnet 4.6 (Meridian)"},
        {"id": "claude-opus-4-6", "name": "Claude Opus 4.6 (Meridian)"}
      ]
    }
  }
}
```

---

### 8.4 本地 LLM（Gemma 4 31B）

**用途**：小寶 Agent 使用的免費本地模型

| 項目 | 說明 |
|------|------|
| 模型 | dealignai/Gemma-4-31B-JANG_4M-CRACK |
| 推理引擎 | vMLX（macOS Apple Silicon 最佳化） |
| API | OpenAI 相容（`http://localhost:8080/v1`） |
| 硬體需求 | 24GB RAM（最低）、Apple Silicon |
| 成本 | $0（完全本地） |

**啟動指令**
```bash
vmlx serve dealignai/Gemma-4-31B-JANG_4M-CRACK --port 8080
```

---

## 9. 技術棧總覽

| 層級 | 元件 | 技術 |
|------|------|------|
| LLM API | @mariozechner/pi-ai | TypeScript、多供應商 SDK |
| Agent 核心 | @mariozechner/pi-agent-core | TypeScript、狀態機、事件發出 |
| CLI | @mariozechner/pi-coding-agent | TypeScript、Node.js、Session 管理 |
| TUI | @mariozechner/pi-tui | TypeScript、差分渲染 |
| Slack Bot | @mariozechner/pi-mom | TypeScript、Socket Mode、Docker 沙箱 |
| Web UI | @mariozechner/pi-web-ui | Lit Web Components、Tailwind CSS |
| HTTP 橋接 | LinkPi.py | Python、FastAPI、JSONL RPC |
| 小寶 Client | harness/xiaobao.py | Python、OpenAI 相容 API |
| 記憶系統 | pi_startup.py | Python、Markdown 檔案 |
| 本地 LLM | vMLX + Gemma 4 31B | Python、Apple MLX |
| 程式碼品質 | Biome + TypeScript | 靜態分析、格式化 |
| 版本管理 | npm workspaces | 鎖步版本（Lockstep versioning） |

---

## 10. 設定與環境變數

### 10.1 .env

```env
# Email 通知
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=johnnylai92@gmail.com
SMTP_PASSWORD=...
EMAIL_FROM=johnnylai92@gmail.com
EMAIL_TO=johnny@mail.dsic.com.tw
USER_EMAIL=johnny@mail.dsic.com.tw

# Notion 整合
NOTION_TOKEN=ntn_...
NOTION_DATABASE_ID=34caad32675280419295fac5ed2ffdee
```

### 10.2 開發指令（根層級）

| 指令 | 說明 |
|------|------|
| `npm run build` | 依序編譯所有套件 |
| `npm run check` | Biome + TypeScript 型別檢查 |
| `npm run test` | 執行所有套件測試 |
| `npm run dev` | 並行啟動所有套件的 watch 模式 |
| `npm run release:patch` | Patch 版本發布（bug fix + 新功能） |
| `npm run release:minor` | Minor 版本發布（API 破壞性變更） |

> **注意**：在 pi-mono 開發中，`npm run dev`、`npm run build`、`npm test` **禁止直接執行**；必須使用 `npm run check` 取代。

### 10.3 版本管理策略

所有套件採用**鎖步版本**（Lockstep Versioning），每次發布時全部套件同步升版。

- `patch`：Bug fix 與新功能
- `minor`：API 破壞性變更

### 10.4 程式碼規範

| 規範 | 說明 |
|------|------|
| TypeScript | 嚴格模式，不允許 `any`（除非絕對必要） |
| Inline imports | 禁止（`await import()` / 動態 import 型別） |
| 相依性降版 | 禁止（應升版相依套件解決型別錯誤） |
| 向後相容 shim | 禁止（除非使用者明確要求） |
| Keybindings | 禁止硬寫按鍵，必須使用設定物件 |

---

*本文件由 Claude Code 根據 pi-mono 原始碼自動生成，版本 1.0（2026-04-27）。*
