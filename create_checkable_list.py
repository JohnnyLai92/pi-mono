import os, json
from dotenv import load_dotenv
from httpx import Client as HTTPClient
import httpx
import ssl

ssl._create_default_https_context = lambda: ssl._create_unverified_context()

load_dotenv('C:/Projects/github/pi-mono/.env')
token = os.environ['NOTION_TOKEN']

headers = {
    'Authorization': f'Bearer {token}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
}

client = httpx.Client(verify=False, headers=headers)

page_id = '352aad32-6752-8145-944b-e371c604e5fe'

# 先清除現有內容
resp = client.delete(f'https://api.notion.com/v1/blocks/{page_id}/children')
print(f'Delete: {resp.status_code}')

# 建立 Checkable Checklist
children = [
    # 標題
    {
        'object': 'block',
        'type': 'heading_2',
        'heading_2': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Pi Agent LLM Provider 串接能力 Checkable 檢核表'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '請逐項勾選已完成項目，打勾 [x] 或打叉 [ ]'}}]
        }
    },
    
    # ===== 第一區：串接整合能力 =====
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '一、串接整合能力（5 項）'}}]
        }
    },
    {
        'object': 'block',
        'type': 'callout',
        'callout': {
            'icon': {'type': 'emoji', 'emoji': '📋'},
            'rich_text': [{'type': 'text', 'text': {'content': 'P0 優先級'}}]
        }
    },
    
    # 1.1 Notion SSL + DATABASE_ID
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P0-01 修正 Notion DATABASE_ID (錯誤指向)'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  狀態：⚠️ 部分可用 | 缺口：DATABASE_ID 錯誤；SSL proxy 阻擋 httpx；blocks=0'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  對策：5 行修復；確認 NOTION_DATABASE_ID 環境變數；patch httpx SSL 驗證順序'}}]
        }
    },
    
    # 1.2 LINE Bot
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P0-02 LINE Bot 整合'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  狀態：❌ 未實作 | 缺口：無 webhook/messaging API 整合'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  對策：FastAPI + line-bot-sdk；新建 pi-line-bridge 服務；Webhook Endpoint'}}]
        }
    },
    
    # 1.3 Notion Skill 模組化
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P2-01 Notion Skill 模組化'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  狀態：⚠️ 碎片化 | 缺口：scripts/ 下有大量獨立腳本，無統一 Entry point'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  對策：重構為單一 Skill；Agent 啟動時只加載描述，需要時才讀取詳細指令'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P2-02 Email 結構化模板'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  狀態：✅ 穩定 | 缺口：無結構化發送模板；無發送狀態回寫 Notion'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P3-01 Slack Socket Mode 預設化'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  狀態：✅ 穩定 | 缺口：Docker 沙箱選配，非預設'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P3-02 GitHub PR/Issue 追蹤'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  狀態：✅ 穩定 | 缺口：僅 commit/push，無 PR 追蹤或 issue 管理'}}]
        }
    },
    
    # ===== 第二區：記憶管理 =====
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '二、記憶管理（3 項）'}}]
        }
    },
    {
        'object': 'block',
        'type': 'callout',
        'callout': {
            'icon': {'type': 'emoji', 'emoji': '🧠'},
            'rich_text': [{'type': 'text', 'text': {'content': 'P1 優先級'}}]
        }
    },
    
    # 2.1 STM 抽取引擎
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P1-01 STM 抽取引擎完工'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  狀態：⚠️ 不可靠 | 缺口：Agent 可能幻覺或中斷導致遺失；fallback 靠 claude -p 補生成，有延遲'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  對策：從 Agent 自願寫入改為 session.jsonl 自動抽取；修復 regex + TypeError + 去重 bug'}}]
        }
    },
    
    # 2.2 LTM 版本歷史
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P2-03 LTM 版本歷史'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  狀態：✅ 11 個主題檔 | 缺口：無版本歷史；衝突合併靠人工確認，缺自動 diff'}}]
        }
    },
    
    # 2.3 APPEND_SYSTEM.md token 上限
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P2-04 APPEND_SYSTEM.md token 上限保護'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  狀態：✅ 每次啟動重建 | 缺口：無長度控管，過多 STM 累積可能超出 context window'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  對策：加入 token 計數上限，超出時截斷較舊 STM 摘要'}}]
        }
    },
    
    # 2.4 跨 Session 記憶語義檢索
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P2-05 跨 Session 語義檢索'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  狀態：✅ 可用 | 缺口：~/.linkpi/memory.md 純文字摘要；無語義檢索'}}]
        }
    },
    
    # ===== 第三區：智識管理 =====
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '三、智識管理（3 項）'}}]
        }
    },
    {
        'object': 'block',
        'type': 'callout',
        'callout': {
            'icon': {'type': 'emoji', 'emoji': '🧠'},
            'rich_text': [{'type': 'text', 'text': {'content': 'P1 優先級'}}]
        }
    },
    
    # 3.1 RAG 檢索
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P1-02 引入 RAG 檢索'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  狀態：❌ 無 | 缺口：無向量資料庫或語義搜尋；只能靠 grep'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  對策：將 ~/.pi/memory/ 轉為向量索引；建立 search_memory 工具；Agent 按需查詢'}}]
        }
    },
    
    # 3.2 Notion on-demand 查詢
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P2-06 Notion on-demand 查詢工具'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  狀態：⚠️ 啟動時單次 | 缺口：無 on-demand 查詢工具；無法在對話中動態搜尋'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  對策：將 notion_reader.py 包裝為 pi 可呼叫的工具（bash 腳本形式）'}}]
        }
    },
    
    # 3.3 Skill registry 動態化
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P3-03 Skill registry 動態化'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  狀態：⚠️ 靜態清單 | 缺口：僅有 SK-01；無動態 skill registry'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  對策：設計 skill discovery 機制；Agent 動態加載可用技能'}}]
        }
    },
    
    # ===== 第四區：LLM Provider 能力 =====
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '四、LLM Provider 能力（基礎健全，4 項）'}}]
        }
    },
    {
        'object': 'block',
        'type': 'callout',
        'callout': {
            'icon': {'type': 'emoji', 'emoji': '🤖'},
            'rich_text': [{'type': 'text', 'text': {'content': '✅ 已健全 - 僅需持續維護'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] MAINT-01 11 個 Provider 覆蓋度確認'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  狀態：✅ 完整 | Anthropic、OpenAI (3 API)、Google (3 API)、Bedrock、Mistral、Faux、xAI、Groq'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] MAINT-02 Streaming 支援確認'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  狀態：✅ 支援 | 所有 Provider 都實作 AssistantMessageEventStream'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] MAINT-03 Tool Call 統一處理'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  狀態：✅ 支援 | 透過 transform-messages 統一處理'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] MAINT-04 Thinking/Reasoning 補實作 Faux + Google CLI'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  狀態：⚠️ 9/11 | Faux 與 Google CLI 未實作'}}]
        }
    },
    
    # ===== 第五區：核心架構缺口 =====
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '五、核心架構缺口（4 項）'}}]
        }
    },
    {
        'object': 'block',
        'type': 'callout',
        'callout': {
            'icon': {'type': 'emoji', 'emoji': '🚨'},
            'rich_text': [{'type': 'text', 'text': {'content': 'P0 最優先修復'}}]
        }
    },
    
    # 5.1 Agent 可靠性
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P0-05 Agent 可靠性強化'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  狀態：P0 致命 | 缺口：Agent 幻覺執行（偽造 claude -p 輸出）是信任危機'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  對策：pi_startup.py 的 capture_session_to_stm() 加入驗證；比對 session.jsonl 實際工具呼叫記錄'}}]
        }
    },
    
    # 5.2 無狀態 Notion 整合
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P1-03 無狀態 Notion 整合'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  狀態：P1 嚴重 | 缺口：啟動時一次性拉取，對話中無法主動查詢'}}]
        }
    },
    
    # 5.3 Rate Limiting
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P1-04 API Rate Limiting'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  狀態：P1 嚴重 | 缺口：API 用量控制未實作'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  對策：Agent 層實作 token bucket 或 sliding window；限制同時併發呼叫'}}]
        }
    },
    
    # 5.4 工具集不對等
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P2-07 工具集不對等'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  狀態：⚠️ 小寶工具集受限 | 缺口：xiaobao.py ACTION 文字解析脆弱（非結構化）'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  對策：改用 JSON RPC 格式統一工具呼叫協議'}}]
        }
    },
    
    # 第六區：統一適配層
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '六、統一適配層（1 項）'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P2-08 統一消息適配層 (Adapter Pattern)'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  缺口：Slack 邏輯硬編碼在 mom 中，擴展 LINE 需重寫大量適配邏輯'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  對策：抽離 Slack/LINE 共通邏輯（權限校驗、歷史記錄格式化）'}}]
        }
    },
    
    # 結尾統計
    {
        'object': 'block',
        'type': 'callout',
        'callout': {
            'icon': {'type': 'emoji', 'emoji': '📊'},
            'rich_text': [{'type': 'text', 'text': {'content': '總結：共 22 項檢查點 | P0: 5 項 | P1: 5 項 | P2: 7 項 | P3: 2 項 | MAINT: 4 項'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '建議順序：先完成 P0 全部 → P1 → P2 → P3 → 日常維護'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '報告日期：2026-04-30 | 分析來源：Claude + Gemini'}}]
        }
    }
]

resp = client.patch(f'https://api.notion.com/v1/blocks/{page_id}/children', json={'children': children})
print(f'Status: {resp.status_code}')
if resp.status_code == 200:
    data = resp.json()
    print(f'Blocks created: {len(data.get("results", []))}')
else:
    print(f'Error: {resp.text}')
