# pi-mono 服務框架 Test Harness Report

**產出時間**：2026-04-06 11:25:11  
**執行耗時**：2.36s  
**整體結果**：✅ ALL PASS  
**統計**：94 pass / 0 fail / 1 warn / 0 skip / 122 total

---

## 目錄

1. [✅ Monorepo 結構（Workspace Structure）](#1)
2. [✅ Build 產出物（Dist Artifacts）](#2)
3. [✅ 模組載入（ESM Module Import）](#3)
4. [✅ AI 套件框架（packages/ai）](#4)
5. [✅ 核心工具框架（Coding Agent Core）](#5)
6. [✅ 服務框架（TUI / MOM / Pods / Web-UI）](#6)
7. [✅ 測試清單盤點（Test Inventory）](#7)

---

## 1. ✅ Monorepo 結構（Workspace Structure）
> 10/10 pass  |  0 fail  |  0 warn  |  0 skip

| # | 測試項目 | 結果 | 說明 | 耗時(ms) |
|---|---------|------|------|---------|
| 1 | `根 package.json 存在` | ✅ PASS | name=pi-monorepo  version=0.0.3 | 0.1 |
| 2 | `workspaces 宣告` | ✅ PASS | 6 個 workspace 路徑 | 0.0 |
| 3 | `核心套件目錄完整` | ✅ PASS | 找到：['ai', 'agent', 'tui', 'coding-agent', 'mom', 'pods', 'web-ui'] | 0.1 |
| 4 | `版本一致性（lockstep）` | ✅ PASS | 所有套件均為 v0.64.0（root monorepo: v0.0.3，屬正常設計） | 0.3 |
| 5 | `套件 package.json 完整性` | ✅ PASS | 7 個套件均有 name/version | 0.2 |
| 6 | `npm install 已執行` | ✅ PASS | package-lock.json (286,289 bytes)，node_modules 存在 | 0.0 |
| 7 | `根 scripts 完整性` | ✅ PASS | 找到：['build', 'check', 'clean', 'test'] | 0.0 |
| 8 | `biome.json（程式碼檢查設定）` | ✅ PASS | 895 bytes | 0.0 |
| 9 | `tsconfig 設定` | ✅ PASS | 找到 2 個：['tsconfig.base.json', 'tsconfig.json'] | 0.1 |
| 10 | `Bridge 腳本存在` | ✅ PASS | 找到：['LinkPi.py', 'pi_startup.py'] | 0.0 |

## 2. ✅ Build 產出物（Dist Artifacts）
> 42/42 pass  |  0 fail  |  0 warn  |  0 skip

| # | 測試項目 | 結果 | 說明 | 耗時(ms) |
|---|---------|------|------|---------|
| 1 | `ai/dist/index.js` | ✅ PASS | 518 bytes | 0.0 |
| 2 | `ai/dist/index.d.ts` | ✅ PASS | 1,540 bytes | 0.0 |
| 3 | `ai/dist/stream.js` | ✅ PASS | 975 bytes | 0.0 |
| 4 | `ai/dist/types.js` | ✅ PASS | 44 bytes | 0.0 |
| 5 | `ai/dist/api-registry.js` | ✅ PASS | 1,444 bytes | 0.0 |
| 6 | `ai/dist/models.js` | ✅ PASS | 2,045 bytes | 0.0 |
| 7 | `ai/dist/models.generated.js` | ✅ PASS | 457,982 bytes | 0.0 |
| 8 | `ai/dist/providers/register-builtins.js` | ✅ PASS | 10,136 bytes | 0.0 |
| 9 | `ai/dist/providers/anthropic.js` | ✅ PASS | 31,602 bytes | 0.0 |
| 10 | `ai/dist/providers/faux.js` | ✅ PASS | 14,238 bytes | 0.0 |
| 11 | `ai/dist/env-api-keys.js` | ✅ PASS | 4,832 bytes | 0.0 |
| 12 | `agent/dist/index.js` | ✅ PASS | 210 bytes | 0.0 |
| 13 | `agent/dist/index.d.ts` | ✅ PASS | 152 bytes | 0.0 |
| 14 | `agent/dist/agent.js` | ✅ PASS | 13,978 bytes | 0.0 |
| 15 | `agent/dist/agent-loop.js` | ✅ PASS | 15,997 bytes | 0.0 |
| 16 | `agent/dist/types.js` | ✅ PASS | 44 bytes | 0.0 |
| 17 | `agent/dist/proxy.js` | ✅ PASS | 10,370 bytes | 0.0 |
| 18 | `tui/dist/index.js` | ✅ PASS | 1,915 bytes | 0.0 |
| 19 | `tui/dist/index.d.ts` | ✅ PASS | 2,589 bytes | 0.0 |
| 20 | `tui/dist/tui.js` | ✅ PASS | 42,225 bytes | 0.0 |
| 21 | `tui/dist/terminal.js` | ✅ PASS | 11,606 bytes | 0.0 |
| 22 | `tui/dist/keybindings.js` | ✅ PASS | 6,270 bytes | 0.0 |
| 23 | `tui/dist/keys.js` | ✅ PASS | 43,296 bytes | 0.0 |
| 24 | `coding-agent/dist/index.js` | ✅ PASS | 4,006 bytes | 0.0 |
| 25 | `coding-agent/dist/index.d.ts` | ✅ PASS | 7,340 bytes | 0.0 |
| 26 | `coding-agent/dist/config.js` | ✅ PASS | 7,859 bytes | 0.0 |
| 27 | `coding-agent/dist/cli.js` | ✅ PASS | 448 bytes | 0.0 |
| 28 | `coding-agent/dist/main.js` | ✅ PASS | 31,219 bytes | 0.0 |
| 29 | `coding-agent/dist/core/agent-session.js` | ✅ PASS | 114,518 bytes | 0.0 |
| 30 | `coding-agent/dist/core/auth-storage.js` | ✅ PASS | 13,959 bytes | 0.0 |
| 31 | `coding-agent/dist/core/tools/index.js` | ✅ PASS | 3,872 bytes | 0.0 |
| 32 | `coding-agent/dist/core/session-manager.js` | ✅ PASS | 40,529 bytes | 0.0 |
| 33 | `coding-agent/dist/modes/rpc/rpc-types.js` | ✅ PASS | 211 bytes | 0.0 |
| 34 | `coding-agent/dist/modes/rpc/jsonl.js` | ✅ PASS | 1,562 bytes | 0.0 |
| 35 | `coding-agent/dist/modes/rpc/rpc-mode.js` | ✅ PASS | 22,380 bytes | 0.0 |
| 36 | `mom/dist/agent.js` | ✅ PASS | 33,847 bytes | 0.0 |
| 37 | `mom/dist/main.js` | ✅ PASS | 13,323 bytes | 0.0 |
| 38 | `mom/dist/slack.js` | ✅ PASS | 17,905 bytes | 0.0 |
| 39 | `mom/dist/store.js` | ✅ PASS | 6,429 bytes | 0.0 |
| 40 | `pods/dist/index.js` | ✅ PASS | 85 bytes | 0.0 |
| 41 | `coding-agent/theme JSON 資源` | ✅ PASS | 找到 3 個主題：['theme-schema.json', 'light.json', 'dark.json'] | 0.1 |
| 42 | `coding-agent source maps` | ✅ PASS | 找到 123 個 .js.map | 1.1 |

## 3. ✅ 模組載入（ESM Module Import）
> 13/13 pass  |  0 fail  |  0 warn  |  0 skip

| # | 測試項目 | 結果 | 說明 | 耗時(ms) |
|---|---------|------|------|---------|
| 1 | `import @pi-ai index` | ✅ PASS | OK exports:52 | 85.2 |
| 2 | `import @pi-ai providers/register-builtins` | ✅ PASS | OK apis:6 | 46.1 |
| 3 | `import @pi-ai models.generated` | ✅ PASS | OK providers:23 models:824 | 48.6 |
| 4 | `import @pi-ai faux provider` | ✅ PASS | OK faux exports:5 | 44.2 |
| 5 | `import @pi-agent-core index` | ✅ PASS | OK agent exports:6 | 85.7 |
| 6 | `import @pi-tui index` | ✅ PASS | OK tui exports:verified | 74.7 |
| 7 | `import @pi-coding-agent config` | ✅ PASS | OK version:0.64.0 agentDir:/Users/Johnny/.pi/agent | 47.6 |
| 8 | `import @pi-coding-agent tools` | ✅ PASS | OK tools:undefined | 163.6 |
| 9 | `import @pi-coding-agent auth-storage` | ✅ PASS | OK methods:21 | 111.8 |
| 10 | `import @pi-coding-agent rpc-mode (dist)` | ✅ PASS | OK rpc-mode exports:1 | 115.1 |
| 11 | `import @pi-coding-agent jsonl` | ✅ PASS | OK jsonl roundtrip | 44.5 |
| 12 | `import @pi-mom main` | ✅ PASS | OK mom dist exists | 46.8 |
| 13 | `import @pi-pods dist` | ✅ PASS | OK pods dist exists | 47.4 |

## 4. ✅ AI 套件框架（packages/ai）
> 5/29 pass  |  0 fail  |  1 warn  |  0 skip

| # | 測試項目 | 結果 | 說明 | 耗時(ms) |
|---|---------|------|------|---------|
| 1 | `所有 KnownApi 已註冊` | ✅ PASS | OK all:10 | 46.9 |
| 2 | `模型目錄 Provider 數量` | ✅ PASS | 23 個 provider，共 824 個模型 | 47.1 |
| 3 | `  provider: amazon-bedrock` | ℹ️  INFO | 86 個模型 | 47.6 |
| 4 | `  provider: anthropic` | ℹ️  INFO | 23 個模型 | 47.6 |
| 5 | `  provider: azure-openai-responses` | ℹ️  INFO | 41 個模型 | 47.6 |
| 6 | `  provider: cerebras` | ℹ️  INFO | 4 個模型 | 47.6 |
| 7 | `  provider: github-copilot` | ℹ️  INFO | 24 個模型 | 47.6 |
| 8 | `  provider: google` | ℹ️  INFO | 25 個模型 | 47.6 |
| 9 | `  provider: google-antigravity` | ℹ️  INFO | 9 個模型 | 47.6 |
| 10 | `  provider: google-gemini-cli` | ℹ️  INFO | 6 個模型 | 47.6 |
| 11 | `  provider: google-vertex` | ℹ️  INFO | 13 個模型 | 47.6 |
| 12 | `  provider: groq` | ℹ️  INFO | 18 個模型 | 47.6 |
| 13 | `  provider: huggingface` | ℹ️  INFO | 18 個模型 | 47.6 |
| 14 | `  provider: kimi-coding` | ℹ️  INFO | 2 個模型 | 47.6 |
| 15 | `  provider: minimax` | ℹ️  INFO | 2 個模型 | 47.6 |
| 16 | `  provider: minimax-cn` | ℹ️  INFO | 2 個模型 | 47.6 |
| 17 | `  provider: mistral` | ℹ️  INFO | 26 個模型 | 47.6 |
| 18 | `  provider: openai` | ℹ️  INFO | 41 個模型 | 47.6 |
| 19 | `  provider: openai-codex` | ℹ️  INFO | 9 個模型 | 47.6 |
| 20 | `  provider: opencode` | ℹ️  INFO | 33 個模型 | 47.6 |
| 21 | `  provider: opencode-go` | ℹ️  INFO | 4 個模型 | 47.6 |
| 22 | `  provider: openrouter` | ℹ️  INFO | 249 個模型 | 47.6 |
| 23 | `  provider: vercel-ai-gateway` | ℹ️  INFO | 153 個模型 | 47.6 |
| 24 | `  provider: xai` | ℹ️  INFO | 24 個模型 | 47.6 |
| 25 | `  provider: zai` | ℹ️  INFO | 12 個模型 | 47.6 |
| 26 | `env-api-keys 偵測` | 🔶 WARN | 已設定：(無)  未設定：['anthropic', 'openai', 'google', 'mistral', 'groq', 'amazon-bedrock', 'openrouter', 'xai', 'azure-openai-responses'] | 49.3 |
| 27 | `faux AssistantMessage 建立` | ✅ PASS | OK role:assistant content:1 | 44.2 |
| 28 | `AssistantMessageEventStream 建立` | ✅ PASS | OK stream type:object | 44.3 |
| 29 | `Overflow 工具（isContextOverflow）` | ✅ PASS | OK isContextOverflow + getOverflowPatterns available | 43.6 |

## 5. ✅ 核心工具框架（Coding Agent Core）
> 10/10 pass  |  0 fail  |  0 warn  |  0 skip

| # | 測試項目 | 結果 | 說明 | 耗時(ms) |
|---|---------|------|------|---------|
| 1 | `allToolDefinitions 完整` | ✅ PASS | 7 個工具：['read', 'bash', 'edit', 'write', 'grep', 'find', 'ls'] | 161.8 |
| 2 | `工具定義格式（name/desc/parameters）` | ✅ PASS | OK all 7 tools have name/description/parameters | 162.5 |
| 3 | `Agent 核心匯出完整` | ✅ PASS | OK all 6 agent exports present | 86.0 |
| 4 | `RPC 命令型別完整` | ✅ PASS | 找到 31 種命令：['abort', 'abort_bash', 'abort_retry', 'bash', 'compact', 'cycle_model', 'cycle_thinking_level', 'export_html', 'extension_ui_request', 'ext | 0.3 |
| 5 | `JSONL RPC 序列化 roundtrip` | ✅ PASS | OK 4 RPC commands serialized | 45.6 |
| 6 | `AuthStorage set/get/has/remove` | ✅ PASS | OK set/get/has/remove all work | 127.7 |
| 7 | `VERSION / getAgentDir()` | ✅ PASS | VERSION:0.64.0 agentDir:/Users/Johnny/.pi/agent | 48.0 |
| 8 | `Compaction 模組匯出` | ✅ PASS | OK compaction maxTokens:undefined | 90.1 |
| 9 | `SessionManager 模組` | ✅ PASS | OK session-manager exports:9 CURRENT_SESSION_VERSION,SessionManager,buildSessionContext,findMostRecentSession,getDefaultSessionDir | 54.4 |
| 10 | `SettingsManager 模組` | ✅ PASS | OK settings-manager exports:3 | 56.1 |

## 6. ✅ 服務框架（TUI / MOM / Pods / Web-UI）
> 9/10 pass  |  0 fail  |  0 warn  |  0 skip

| # | 測試項目 | 結果 | 說明 | 耗時(ms) |
|---|---------|------|------|---------|
| 1 | `TUI 核心元件匯出` | ✅ PASS | OK 15 components exported | 75.8 |
| 2 | `TUI_KEYBINDINGS 定義` | ✅ PASS | OK keybindings:31 groups:tui.editor.cursorUp,tui.editor.cursorDown,tui.editor.cursorLeft,tui.editor.cursorRight,tui.editor.cursorWordLeft,tui.editor.c | 74.1 |
| 3 | `TUI fuzzyFilter / fuzzyMatch 功能` | ✅ PASS | OK fuzzyFilter:1 fuzzyMatch.score:-14.1 | 44.6 |
| 4 | `MOM dist 結構` | ✅ PASS | 16 個 .js 檔案：['download.js', 'events.js', 'store.js', 'log.js', 'main.js', 'slack.js'] | 0.4 |
| 5 | `MOM 環境變數清單` | ℹ️  INFO | 需要設定：['MOM_SLACK_APP_TOKEN', 'MOM_SLACK_BOT_TOKEN'] | 0.1 |
| 6 | `MOM Slack Bot 檔案完整` | ✅ PASS | OK all 5 mom files exist | 45.4 |
| 7 | `Pods dist 結構` | ✅ PASS | 9 個 .js 檔案：['types.js', 'index.js', 'config.js', 'ssh.js', 'cli.js', 'model-configs.js'] | 0.3 |
| 8 | `Web-UI dist 結構` | ✅ PASS | 71 個 .js 檔案 | 0.7 |
| 9 | `RPC 模式原始碼完整` | ✅ PASS | 4/4：['rpc-mode.ts', 'rpc-types.ts', 'jsonl.ts', 'rpc-client.ts'] | 0.0 |
| 10 | `pi 可執行腳本` | ✅ PASS | 找到：['pi.sh', 'pi.cmd', 'pi-test.sh'] | 0.0 |

## 7. ✅ 測試清單盤點（Test Inventory）
> 5/8 pass  |  0 fail  |  0 warn  |  0 skip

| # | 測試項目 | 結果 | 說明 | 耗時(ms) |
|---|---------|------|------|---------|
| 1 | `ai 測試數量` | ✅ PASS | 44 個測試檔案  [ai/stream(11)  e2e(1)  infra(2)  other(19)  tools(11)] | 0.4 |
| 2 | `agent 測試數量` | ✅ PASS | 4 個測試檔案  [ai/stream(1)  e2e(1)  session/agent(2)] | 0.1 |
| 3 | `tui 測試數量` | ✅ PASS | 21 個測試檔案  [infra(1)  other(10)  tools(1)  tui(9)] | 0.1 |
| 4 | `coding-agent 測試數量` | ✅ PASS | 78 個測試檔案  [ai/stream(3)  infra(7)  other(37)  session/agent(24)  tools(6)  tui(1)] | 1.0 |
| 5 | `測試檔案總計` | ℹ️  INFO | 共 147 個 .test.ts 檔案 | 0.0 |
| 6 | `vitest 設定檔` | ✅ PASS | 找到 4 個：['packages/coding-agent/vitest.config.ts', 'packages/tui/vitest.config.ts', 'packages/agent/vitest.config.ts', 'packages/ai/vitest.config.ts'] | 0.3 |
| 7 | `test-harness.test.ts（coding-agent 內建 harness）` | ℹ️  INFO | 321 行，10,400 bytes | 0.1 |
| 8 | `rpc.test.ts 測試案例` | ℹ️  INFO | 約 14 個測試案例，321 行 | 0.2 |

---

## 架構總覽（Architecture Overview）

```
pi-mono  (v0.64.0)
├── packages/ai             @mariozechner/pi-ai
│     ├── AI Provider 抽象層（stream / streamSimple）
│     ├── 23+ 個 Provider（Anthropic, OpenAI, Google, Bedrock…）
│     ├── 824 個預設模型（models.generated.js）
│     └── Event Stream 框架
│
├── packages/agent          @mariozechner/pi-agent-core
│     ├── Agent（主控迴圈）
│     ├── agentLoop / runAgentLoop
│     └── streamProxy（代理轉發）
│
├── packages/tui            @mariozechner/pi-tui
│     ├── TUI（終端機 UI 框架）
│     ├── 15+ 個 UI 元件（Box, Editor, Markdown…）
│     └── KeybindingsManager, fuzzySearch
│
├── packages/coding-agent   @mariozechner/pi-coding-agent
│     ├── AgentSession（會話管理）
│     ├── 工具：bash / edit / read / write / find / grep / ls
│     ├── Compaction（上下文壓縮）
│     ├── SessionManager（多分支會話）
│     ├── AuthStorage（認證儲存）
│     ├── RPC 模式（JSONL stdin/stdout 協議）
│     └── 互動模式 / Print 模式
│
├── packages/mom            @mariozechner/pi-mom
│     ├── Multi-agent Orchestration
│     ├── SlackBot 整合
│     └── Sandbox 支援
│
├── packages/pods           @mariozechner/pi
│     └── 部署與封裝工具
│
├── packages/web-ui         @mariozechner/pi-web-ui
│     └── Web 介面
│
└── LinkPi.py               OpenAI 相容 HTTP Bridge
      ├── FastAPI Server（port 8765）
      ├── ProviderRegistry（per-provider PiProcess）
      ├── SharedMemory（跨 Provider 記憶）
      └── Endpoints: /v1/models, /v1/chat/completions,
                     /v1/consolidate, /v1/memory
```

## 測試涵蓋範圍

| Suite | 涵蓋內容 | 方式 |
|-------|---------|------|
| 1. Monorepo 結構 | workspace、版本、scripts、設定檔 | package.json 解析 |
| 2. Build 產出物 | dist/ 目錄、關鍵 .js/.d.ts 檔案 | 檔案系統掃描 |
| 3. 模組載入 | 各套件 ESM import | Node.js --input-type=module |
| 4. AI 套件框架 | provider 註冊、模型目錄、env keys | Node.js eval |
| 5. 核心工具框架 | 工具定義、Agent、RPC、Auth、Compaction | Node.js eval |
| 6. 服務框架 | TUI 元件、MOM、Pods、Web-UI | 檔案 + Node.js eval |
| 7. 測試清單盤點 | 現有 test 檔案統計分類 | glob 掃描 |
| **未涵蓋** | 真實 LLM 呼叫（需 API Key）、E2E 流程 | — |