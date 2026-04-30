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

# 建立完整的檢核表 - 使用表格格式
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
        'type': 'table',
        'table': {
            'table_width': 4,
            'has_column_header': True,
            'children': [
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': '能力項目'}}],
                            [{'type': 'text', 'text': {'content': '狀態'}}],
                            [{'type': 'text', 'text': {'content': '缺口'}}],
                            [{'type': 'text', 'text': {'content': '優先級'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'Notion 讀寫'}}],
                            [{'type': 'text', 'text': {'content': '⚠️ 部分可用'}}],
                            [{'type': 'text', 'text': {'content': 'DATABASE_ID 錯誤；SSL proxy 阻擋 httpx；blocks=0'}}],
                            [{'type': 'text', 'text': {'content': 'P0'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'Email (SMTP)'}}],
                            [{'type': 'text', 'text': {'content': '✅ 穩定'}}],
                            [{'type': 'text', 'text': {'content': '無結構化發送模板；無發送狀態回寫 Notion'}}],
                            [{'type': 'text', 'text': {'content': 'P2'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'LINE Bot'}}],
                            [{'type': 'text', 'text': {'content': '❌ 未實作'}}],
                            [{'type': 'text', 'text': {'content': '無 webhook/messaging API 整合'}}],
                            [{'type': 'text', 'text': {'content': 'P0'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'Slack (Socket Mode)'}}],
                            [{'type': 'text', 'text': {'content': '✅ 穩定'}}],
                            [{'type': 'text', 'text': {'content': 'Docker 沙箱選配，非預設'}}],
                            [{'type': 'text', 'text': {'content': 'P3'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'GitHub auto-sync'}}],
                            [{'type': 'text', 'text': {'content': '✅ 穩定'}}],
                            [{'type': 'text', 'text': {'content': '僅 commit/push，無 PR 追蹤或 issue 管理'}}],
                            [{'type': 'text', 'text': {'content': 'P3'}}]
                        ]
                    }
                }
            ]
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
        'type': 'table',
        'table': {
            'table_width': 4,
            'has_column_header': True,
            'children': [
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': '能力項目'}}],
                            [{'type': 'text', 'text': {'content': '狀態'}}],
                            [{'type': 'text', 'text': {'content': '缺口'}}],
                            [{'type': 'text', 'text': {'content': '優先級'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'STM 寫入'}}],
                            [{'type': 'text', 'text': {'content': '⚠️ 不可靠'}}],
                            [{'type': 'text', 'text': {'content': 'Agent 可能幻覺或中斷導致遺失；fallback 靠 claude -p 補生成，有延遲'}}],
                            [{'type': 'text', 'text': {'content': 'P1'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'LTM 結構'}}],
                            [{'type': 'text', 'text': {'content': '✅ 11 個主題檔'}}],
                            [{'type': 'text', 'text': {'content': '無版本歷史；衝突合併靠人工確認，缺自動 diff'}}],
                            [{'type': 'text', 'text': {'content': 'P2'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': '跨 Session 記憶'}}],
                            [{'type': 'text', 'text': {'content': '✅ 可用'}}],
                            [{'type': 'text', 'text': {'content': '~/.linkpi/memory.md 純文字摘要；無語義檢索'}}],
                            [{'type': 'text', 'text': {'content': 'P2'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'APPEND_SYSTEM.md'}}],
                            [{'type': 'text', 'text': {'content': '✅ 每次啟動重建'}}],
                            [{'type': 'text', 'text': {'content': '無長度控管，過多 STM 累積可能超出 context window'}}],
                            [{'type': 'text', 'text': {'content': 'P2'}}]
                        ]
                    }
                }
            ]
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
        'type': 'table',
        'table': {
            'table_width': 4,
            'has_column_header': True,
            'children': [
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': '能力項目'}}],
                            [{'type': 'text', 'text': {'content': '狀態'}}],
                            [{'type': 'text', 'text': {'content': '缺口'}}],
                            [{'type': 'text', 'text': {'content': '優先級'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'Notion 任務查詢'}}],
                            [{'type': 'text', 'text': {'content': '⚠️ 啟動時單次'}}],
                            [{'type': 'text', 'text': {'content': '無 on-demand 查詢工具；無法在對話中動態搜尋'}}],
                            [{'type': 'text', 'text': {'content': 'P2'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'Skill 檢索'}}],
                            [{'type': 'text', 'text': {'content': '⚠️ 靜態清單'}}],
                            [{'type': 'text', 'text': {'content': '僅有 SK-01；無動態 skill registry'}}],
                            [{'type': 'text', 'text': {'content': 'P3'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': '問題索引查詢'}}],
                            [{'type': 'text', 'text': {'content': '❌ 未完成'}}],
                            [{'type': 'text', 'text': {'content': '第三階段（查詢介面）尚未開發'}}],
                            [{'type': 'text', 'text': {'content': 'P1'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': '知識庫搜尋'}}],
                            [{'type': 'text', 'text': {'content': '❌ 無'}}],
                            [{'type': 'text', 'text': {'content': '無向量資料庫或語義搜尋；只能靠 grep'}}],
                            [{'type': 'text', 'text': {'content': 'P1'}}]
                        ]
                    }
                }
            ]
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
        'type': 'table',
        'table': {
            'table_width': 4,
            'has_column_header': True,
            'children': [
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': '能力項目'}}],
                            [{'type': 'text', 'text': {'content': '狀態'}}],
                            [{'type': 'text', 'text': {'content': '說明'}}],
                            [{'type': 'text', 'text': {'content': '優先級'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': '11 個 Provider'}}],
                            [{'type': 'text', 'text': {'content': '✅ 完整'}}],
                            [{'type': 'text', 'text': {'content': 'Anthropic、OpenAI (3 API)、Google (3 API)、Bedrock、Mistral、Faux'}}],
                            [{'type': 'text', 'text': {'content': '-'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'Streaming'}}],
                            [{'type': 'text', 'text': {'content': '✅ 支援'}}],
                            [{'type': 'text', 'text': {'content': '所有 Provider 都實作 AssistantMessageEventStream'}}],
                            [{'type': 'text', 'text': {'content': '-'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'Tool Call'}}],
                            [{'type': 'text', 'text': {'content': '✅ 支援'}}],
                            [{'type': 'text', 'text': {'content': '透過 transform-messages 統一處理'}}],
                            [{'type': 'text', 'text': {'content': '-'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'Thinking/Reasoning'}}],
                            [{'type': 'text', 'text': {'content': '⚠️ 9/11'}}],
                            [{'type': 'text', 'text': {'content': 'Faux 與 Google CLI 未實作'}}],
                            [{'type': 'text', 'text': {'content': '-'}}]
                        ]
                    }
                }
            ]
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
        'type': 'table',
        'table': {
            'table_width': 4,
            'has_column_header': True,
            'children': [
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': '缺口'}}],
                            [{'type': 'text', 'text': {'content': '嚴重性'}}],
                            [{'type': 'text', 'text': {'content': '說明'}}],
                            [{'type': 'text', 'text': {'content': '對策'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'Agent 可靠性'}}],
                            [{'type': 'text', 'text': {'content': 'P0 致命'}}],
                            [{'type': 'text', 'text': {'content': 'Agent 幻覺執行（偽造 claude -p 輸出）是信任危機'}}],
                            [{'type': 'text', 'text': {'content': 'pi_startup.py 驗證 session.jsonl 工具呼叫記錄'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': '無狀態的 Notion 整合'}}],
                            [{'type': 'text', 'text': {'content': 'P1 嚴重'}}],
                            [{'type': 'text', 'text': {'content': '啟動時一次性拉取，對話中無法主動查詢'}}],
                            [{'type': 'text', 'text': {'content': '將 notion_reader.py 包裝為 pi 可呼叫的工具'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': '無 Rate Limiting'}}],
                            [{'type': 'text', 'text': {'content': 'P1 嚴重'}}],
                            [{'type': 'text', 'text': {'content': 'API 用量控制未實作'}}],
                            [{'type': 'text', 'text': {'content': 'Agent 層實作 token bucket 或 sliding window'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'Context 膨脹風險'}}],
                            [{'type': 'text', 'text': {'content': 'P2 一般'}}],
                            [{'type': 'text', 'text': {'content': 'APPEND_SYSTEM.md 過多可能超出 context window'}}],
                            [{'type': 'text', 'text': {'content': '加入 token 計數上限保護'}}]
                        ]
                    }
                }
            ]
        }
    },
    
    # 第六區：綜合優先級排序
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '六、綜合優先級排序'}}]
        }
    },
    {
        'object': 'block',
        'type': 'table',
        'table': {
            'table_width': 3,
            'has_column_header': True,
            'children': [
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': '優先級'}}],
                            [{'type': 'text', 'text': {'content': '項目'}}],
                            [{'type': 'text', 'text': {'content': '備註'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'P0'}}],
                            [{'type': 'text', 'text': {'content': '修正 Notion DATABASE_ID + SSL patch'}}],
                            [{'type': 'text', 'text': {'content': '每天都阻斷任務查詢，5 行修復'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'P0'}}],
                            [{'type': 'text', 'text': {'content': 'LINE Bot 整合'}}],
                            [{'type': 'text', 'text': {'content': '使用者核心需求，FastAPI + line-bot-sdk'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'P1'}}],
                            [{'type': 'text', 'text': {'content': 'STM 抽取引擎完工'}}],
                            [{'type': 'text', 'text': {'content': 'session.jsonl 自動抽取，修復 regex + TypeError + 去重'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'P1'}}],
                            [{'type': 'text', 'text': {'content': '引入 RAG 檢索'}}],
                            [{'type': 'text', 'text': {'content': '向量索引取代全量注入'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'P2'}}],
                            [{'type': 'text', 'text': {'content': 'Notion Skill 模組化'}}],
                            [{'type': 'text', 'text': {'content': '重構 scripts/ 腳本為統一 Skill'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'P2'}}],
                            [{'type': 'text', 'text': {'content': 'APPEND_SYSTEM.md token 上限保護'}}],
                            [{'type': 'text', 'text': {'content': '防止 context overflow 的預防性修復'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'P3'}}],
                            [{'type': 'text', 'text': {'content': 'Skill registry 動態化'}}],
                            [{'type': 'text', 'text': {'content': '需設計 skill discovery 機制'}}]
                        ]
                    }
                }
            ]
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
