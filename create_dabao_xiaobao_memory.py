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

# 建立大寶小寶記憶分析頁面
children = [
    # 標題
    {
        'object': 'block',
        'type': 'heading_2',
        'heading_2': {
            'rich_text': [{'type': 'text', 'text': {'content': '大寶 vs 小寶 記憶架構分析'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '針對雙 Agent 架構（大寶 Gemma、小寶 OpenAI）的記憶管理機制進行分析'}}]
        }
    },
    
    # ===== 大寶（Gemma）記憶架構 =====
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '一、大寶（Gemma）記憶架構'}}]
        }
    },
    {
        'object': 'block',
        'type': 'callout',
        'callout': {
            'icon': {'type': 'emoji', 'emoji': '🤖'},
            'rich_text': [{'type': 'text', 'text': {'content': '本地 LLM - 輕量級 Agent'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '## 記憶路徑'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'LSTM（長效記憶）：~/.pi/memory/ 共用 11 個主題檔'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'STM（短期記憶）：~/.pi/agent/sessions/{slug}/ 下的 session.jsonl'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '跨 Session：無獨立記憶檔案，依賴 LTM 共享'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '## 記憶能力'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '✅ 可讀取 ~/.pi/memory/ 下的 LTM 檔案'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '✅ 可寫入 session.jsonl（透過 pi_startup.py）'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '⚠️ 工具集受限：xiaobao.py 的 ACTION 文字解析脆弱'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '❌ 無獨立記憶管理工具：無法主動查詢或更新 LTM'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '## 記憶缺口'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '無 vMLX 自動重啟：手動啟動後可能失效'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '無跨 Provider 記憶共享：僅透過 ~/.linkpi/memory.md 純文字摘要'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '無語義檢索：只能靠 grep，無法進行向量搜尋'}}]
        }
    },
    
    # ===== 小寶（OpenAI）記憶架構 =====
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '二、小寶（OpenAI）記憶架構'}}]
        }
    },
    {
        'object': 'block',
        'type': 'callout',
        'callout': {
            'icon': {'type': 'emoji', 'emoji': '🤖'},
            'rich_text': [{'type': 'text', 'text': {'content': '主線 LLM - 全功能 Agent'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '## 記憶路徑'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'LSTM（長效記憶）：~/.pi/memory/ 共用 11 個主題檔'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'STM（短期記憶）：~/.pi/agent/sessions/{slug}/ 下的 session.jsonl'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '跨 Session：~/.linkpi/memory.md 純文字摘要'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '## 記憶能力'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '✅ 可讀取 ~/.pi/memory/ 下的 LTM 檔案'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '✅ 可執行 bash 工具調用各種腳本'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '✅ 可透過 httpx 呼叫 Notion API'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '✅ 可透過 Claude Code Review 驗證輸出'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '⚠️ STM 寫入不可靠：Agent 可能幻覺或中斷導致遺失'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '## 記憶缺口'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '無 on-demand Notion 查詢：啟動時一次性拉取'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '無 Rate Limiting：API 用量控制未實作'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '無 RAG 檢索：只能靠 grep 或全量注入'}}]
        }
    },
    
    # ===== 跨 Agent 記憶共享機制 =====
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '三、跨 Agent 記憶共享機制'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '## 共享路徑'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '~/.pi/memory/：LTM 共用（11 個主題檔）'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '~/.pi/agent/sessions/{slug}/：session.jsonl 共用'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '~/.linkpi/memory.md：跨 Provider 轉移摘要'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '## 轉移流程'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '大寶 → 小寶：透過 LinkPi.py 進行 Handoff Summary'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '小寶 → 大寶：透過 LinkPi.py 進行 Handoff Summary'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '每次啟動 pi 時，自動合併 STM/LTM 至 APPEND_SYSTEM.md'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '## 記憶轉移缺口'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '~/.linkpi/memory.md 為純文字摘要，無語義檢索'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '無版本歷史：衝突合併靠人工確認'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '無跨 Agent 衝突偵測：兩 Agent 可能同時修改同一檔案'}}]
        }
    },
    
    # ===== 大寶 vs 小寶 記憶能力對比 =====
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '四、大寶 vs 小寶 記憶能力對比'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'table',
        'table': {
            'table_width': 5,
            'has_column_header': True,
            'children': [
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': '記憶維度'}}],
                            [{'type': 'text', 'text': {'content': '大寶（Gemma）'}}],
                            [{'type': 'text', 'text': {'content': '小寶（OpenAI）'}}],
                            [{'type': 'text', 'text': {'content': '共享'}}],
                            [{'type': 'text', 'text': {'content': '優先級'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'LTM 讀取'}}],
                            [{'type': 'text', 'text': {'content': '✅'}}],
                            [{'type': 'text', 'text': {'content': '✅'}}],
                            [{'type': 'text', 'text': {'content': '~/.pi/memory/'}}],
                            [{'type': 'text', 'text': {'content': '-'}}]
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
                            [{'type': 'text', 'text': {'content': '⚠️ 不可靠'}}],
                            [{'type': 'text', 'text': {'content': 'session.jsonl'}}],
                            [{'type': 'text', 'text': {'content': 'P1'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': '跨 Session 記憶'}}],
                            [{'type': 'text', 'text': {'content': '⚠️ 無'}}],
                            [{'type': 'text', 'text': {'content': '✅ 透過 LinkPi'}}],
                            [{'type': 'text', 'text': {'content': '~/.linkpi/memory.md'}}],
                            [{'type': 'text', 'text': {'content': 'P2'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': '語義檢索'}}],
                            [{'type': 'text', 'text': {'content': '❌ 無'}}],
                            [{'type': 'text', 'text': {'content': '❌ 無'}}],
                            [{'type': 'text', 'text': {'content': '無'}}],
                            [{'type': 'text', 'text': {'content': 'P1'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': '工具集'}}],
                            [{'type': 'text', 'text': {'content': '⚠️ 受限'}}],
                            [{'type': 'text', 'text': {'content': '✅ 完整'}}],
                            [{'type': 'text', 'text': {'content': 'bash 工具'}}],
                            [{'type': 'text', 'text': {'content': 'P2'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'Notion 操作'}}],
                            [{'type': 'text', 'text': {'content': '⚠️ 有限'}}],
                            [{'type': 'text', 'text': {'content': '✅ 完整'}}],
                            [{'type': 'text', 'text': {'content': 'httpx API'}}],
                            [{'type': 'text', 'text': {'content': 'P0'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'Claude Code Review'}}],
                            [{'type': 'text', 'text': {'content': '⚠️ 受限'}}],
                            [{'type': 'text', 'text': {'content': '✅ 可用'}}],
                            [{'type': 'text', 'text': {'content': 'claude -p'}}],
                            [{'type': 'text', 'text': {'content': 'P0'}}]
                        ]
                    }
                }
            ]
        }
    },
    
    # ===== 建議的改進方案 =====
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '五、建議的改進方案'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P0-01 Agent 可靠性強化'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  對策：pi_startup.py 的 capture_session_to_stm() 加入驗證；比對 session.jsonl 實際工具呼叫記錄'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P1-01 語義檢索（RAG）'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  對策：將 ~/.pi/memory/ 和 ~/.linkpi/memory.md 轉為向量索引；建立 search_memory 工具'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P2-01 工具集統一（JSON RPC）'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  對策：xiaobao.py 改用 JSON RPC 格式統一工具呼叫協議'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P2-02 跨 Agent 衝突偵測'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  對策：在 LTM 寫入時加入版本號或 timestamp 檢查；衝突時提示人工確認'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'to_do',
        'to_do': {
            'rich_text': [{'type': 'text', 'text': {'content': '[ ] P2-03 APPEND_SYSTEM.md token 上限'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '  對策：加入 token 計數上限，超出時截斷較舊 STM 摘要'}}]
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
