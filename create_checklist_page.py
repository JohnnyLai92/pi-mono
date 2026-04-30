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

# 建立完整的檢核表
children = [
    # 標題
    {
        'object': 'block',
        'type': 'heading_2',
        'heading_2': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Pi Agent LLM Provider 串接能力檢核表'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '本檢核表彙整 Claude 與 Gemini 建議，針對 Pi Agent 架構進行能力評估。'}}]
        }
    },
    
    # 第一區：串接整合能力
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '一、串接整合能力'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Notion 讀寫 | ⚠️ 部分可用 | DATABASE_ID 錯誤；SSL proxy 阻擋 httpx；blocks=0 | P0'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Email (SMTP) | ✅ 穩定 | 無結構化發送模板；無發送狀態回寫 Notion | P2'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'LINE Bot | ❌ 未實作 | 無 webhook/messaging API 整合 | P0'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Slack (Socket Mode) | ✅ 穩定 | Docker 沙箱選配，非預設 | P3'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'GitHub auto-sync | ✅ 穩定 | 僅 commit/push，無 PR 追蹤或 issue 管理 | P3'}}]
        }
    },
    
    # 第二區：記憶管理
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '二、記憶管理'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'STM 寫入 | ⚠️ 不可靠 | Agent 可能幻覺或中斷導致遺失；fallback 靠 claude -p 補生成，有延遲 | P1'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'LTM 結構 | ✅ 11 個主題檔 | 無版本歷史；衝突合併靠人工確認，缺自動 diff | P2'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '跨 Session 記憶 | ✅ 可用 | ~/.linkpi/memory.md 純文字摘要；無語義檢索 | P2'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '改進方向：STM 應從 Agent 自願寫入改為 session.jsonl 自動抽取'}}]
        }
    },
    
    # 第三區：智識管理
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '三、智識管理'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Notion 任務查詢 | ⚠️ 啟動時單次 | 無 on-demand 查詢工具；無法在對話中動態搜尋 | P2'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Skill 檢索 | ⚠️ 靜態清單 | 僅有 SK-01；無動態 skill registry | P3'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '知識庫搜尋 | ❌ 無 | 無向量資料庫或語義搜尋；只能靠 grep | P1'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '改進方向：引入 RAG 檢索，將 ~/.pi/memory/ 轉為向量索引'}}]
        }
    },
    
    # 第四區：LLM Provider 串接能力
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '四、LLM Provider 串接能力'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '11 個 Provider | ✅ 完整 | Anthropic、OpenAI (3 API)、Google (3 API)、Bedrock、Mistral、Faux | -'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Streaming | ✅ 支援 | 所有 Provider 都實作 AssistantMessageEventStream | -'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Tool Call | ✅ 支援 | 透過 transform-messages 統一處理 | -'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Thinking/Reasoning | ⚠️ 9/11 | Faux 與 Google CLI 未實作 | -'}}]
        }
    },
    
    # 第五區：核心架構缺口
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '五、核心架構缺口'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Agent 可靠性：Agent 幻覺執行（偽造 claude -p 輸出）是信任危機 | P0'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Context 膨脹風險：APPEND_SYSTEM.md 過多可能超出 context window | P2'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '無狀態的 Notion 整合：啟動時一次性拉取，對話中無法主動查詢 | P1'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '無 Rate Limiting：API 用量控制未實作 | P1'}}]
        }
    },
    
    # 第六區：建議的優先級排序
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '六、綜合優先級排序'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'P0：修正 Notion DATABASE_ID + SSL patch（每天都阻斷任務查詢）'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'P0：LINE Bot 整合（使用者核心需求，FastAPI + line-bot-sdk）'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'P1：STM 抽取引擎完工（session.jsonl 自動抽取）'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'P1：引入 RAG 檢索（向量索引取代全量注入）'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'P2：Notion Skill 模組化（重構 scripts/ 腳本為統一 Skill）'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'P2：APPEND_SYSTEM.md token 上限保護'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'P3：Skill registry 動態化'}}]
        }
    },
    
    # 結尾
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
