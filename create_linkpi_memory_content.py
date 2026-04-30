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

# 建立大寶小寶實際記憶內容頁面
children = [
    # 標題
    {
        'object': 'block',
        'type': 'heading_2',
        'heading_2': {
            'rich_text': [{'type': 'text', 'text': {'content': '~/.linkpi/memory.md 實際記憶內容'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '檔案路徑：C:/Users/johnny/.linkpi/memory.md | 總記錄數：5 筆 | 分析日期：2026-04-30'}}]
        }
    },
    
    # ===== 大寶記憶 =====
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '一、大寶（local-llm）記憶內容（1 筆）'}}]
        }
    },
    {
        'object': 'block',
        'type': 'callout',
        'callout': {
            'icon': {'type': 'emoji', 'emoji': '🤖'},
            'rich_text': [{'type': 'text', 'text': {'content': '日期：20260401-163409 | 記憶標題：model ID 與身份確認'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Goal: User wants to understand the AI assistant model ID and identity. User requests the assistant to exclusively respond in Traditional Chinese and follow AGENTS.md guidelines.'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Constraints: Respond exclusively in Traditional Chinese. Follow guidelines in pi-mono AGENTS.md.'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Progress Done: [x] Identified and responded to user model ID inquiry. [x] Confirmed understanding of user language preference for responses. [x] Acknowledged understanding of pi-mono AGENTS.md guidelines for future interactions.'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Progress In Progress: [ ] Implementing adherence to AGENTS.md guidelines.'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Key Decisions: Language Preference - User requires all responses in Traditional Chinese. Compliance - Assistant will follow pi-mono AGENTS.md guidelines for future interactions.'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Next Steps: 1. Verify AGENTS.md content to ensure full compliance. 2. Implement language enforcement for all future responses. 3. Document the language preference requirement for future reference.'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Critical Context: User has requested exclusive use of Traditional Chinese in responses. Need to reference pi-mono AGENTS.md for compliance standards.'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'heading_4',
        'heading_4': {
            'rich_text': [{'type': 'text', 'text': {'content': '大寶記憶分析'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '記憶內容：model ID 查詢與身份確認、繁體中文偏好設定'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '記憶結構：標準的 Goal/Constraints/Progress/Decisions/Next Steps 格式'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '記憶狀態：[ ] 未完成的任務（Implementing adherence to AGENTS.md）'}}]
        }
    },
    
    # ===== 小寶記憶 =====
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '二、小寶（Anthropic）記憶內容（1 筆）'}}]
        }
    },
    {
        'object': 'block',
        'type': 'callout',
        'callout': {
            'icon': {'type': 'emoji', 'emoji': '❌'},
            'rich_text': [{'type': 'text', 'text': {'content': '日期：20260401-152333 | 記憶狀態：空內容錯誤，無實際有效記憶'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '錯誤訊息：I notice that you have provided an empty conversation container <conversation></conversation>. There is no actual conversation content for me to summarize.'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '要求提供的內容：The actual conversation between a user and AI coding assistant. Information about their goals, tasks, code changes, decisions, etc.'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '狀態：❌ 無效記錄（empty conversation），無法產生有意義的結構化摘要'}}]
        }
    },
    
    # ===== Pi Agent 記憶 =====
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '三、Pi Agent 記憶內容（3 筆）'}}]
        }
    },
    {
        'object': 'block',
        'type': 'callout',
        'callout': {
            'icon': {'type': 'emoji', 'emoji': '📋'},
            'rich_text': [{'type': 'text', 'text': {'content': '記憶主題：Structured Context Checkpoint Summary 請求（全為空內容）'}}]
        }
    },
    
    # Pi Agent #1
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '--- Pi Agent #1 (20260401-163507) ---'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Goal: The user wants to create a structured context checkpoint summary for an AI coding assistant to continue work on a conversation that has no content.'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Constraints: The summary must follow the exact specified format. Only output the structured summary without continuing the conversation. Must preserve file paths, function names, and error messages if present.'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Progress: [x] Received request for structured summary of empty conversation. [x] Prepared structured summary in required format.'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Key Decisions: Format Selection - Used exact format specification provided by user. Content Handling - Since conversation is empty, created minimal valid structure.'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Critical Context: The conversation contains no messages to summarize. The assistant is responding to a request for a summary of an empty conversation. No files, functions, or code changes are relevant to this task.'}}]
        }
    },
    
    # Pi Agent #2
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '--- Pi Agent #2 (20260402-114430) ---'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Goal: [Unknown - No conversation provided to summarize.]'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Progress: [x] (none) / [ ] Waiting for initial user prompt or task description.'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Key Decisions: None - No decisions have been made yet as the conversation context is empty.'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Next Steps: Await user input to establish project context, goals, and initial tasks.'}}]
        }
    },
    
    # Pi Agent #3
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '--- Pi Agent #3 (20260402-165231) ---'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': 'I notice that the conversation content is empty - there are no messages between a user and AI coding assistant to summarize.'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Without any conversation content to analyze, I cannot create a meaningful structured summary following the specified format.'}}]
        }
    },
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': 'If you have a conversation to summarize, please provide the actual message content.'}}]
        }
    },
    
    # ===== 統計分析 =====
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '四、統計分析'}}]
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
                            [{'type': 'text', 'text': {'content': '維度'}}],
                            [{'type': 'text', 'text': {'content': '值'}}],
                            [{'type': 'text', 'text': {'content': '說明'}}],
                            [{'type': 'text', 'text': {'content': '狀態'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': '總記錄數'}}],
                            [{'type': 'text', 'text': {'content': '5 筆'}}],
                            [{'type': 'text', 'text': {'content': '~/.linkpi/memory.md 總計'}}],
                            [{'type': 'text', 'text': {'content': '-'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': '大寶有效記錄'}}],
                            [{'type': 'text', 'text': {'content': '1 筆'}}],
                            [{'type': 'text', 'text': {'content': '20260401-163409，有實質內容'}}],
                            [{'type': 'text', 'text': {'content': '✅'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': '小寶有效記錄'}}],
                            [{'type': 'text', 'text': {'content': '0 筆'}}],
                            [{'type': 'text', 'text': {'content': '空內容錯誤訊息，無實際記憶'}}],
                            [{'type': 'text', 'text': {'content': '❌'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': 'Pi Agent 有效記錄'}}],
                            [{'type': 'text', 'text': {'content': '0 筆'}}],
                            [{'type': 'text', 'text': {'content': '3 筆全為空內容請求'}}],
                            [{'type': 'text', 'text': {'content': '❌'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': '有效記憶率'}}],
                            [{'type': 'text', 'text': {'content': '20% (1/5)'}}],
                            [{'type': 'text', 'text': {'content': '僅大寶有實質記憶內容'}}],
                            [{'type': 'text', 'text': {'content': '⚠️'}}]
                        ]
                    }
                },
                {
                    'object': 'block',
                    'type': 'table_row',
                    'table_row': {
                        'cells': [
                            [{'type': 'text', 'text': {'content': '記憶跨度'}}],
                            [{'type': 'text', 'text': {'content': '2026-04-01 ~ 2026-04-02'}}],
                            [{'type': 'text', 'text': {'content': '僅有 2 天記錄'}}],
                            [{'type': 'text', 'text': {'content': '⚠️'}}]
                        ]
                    }
                }
            ]
        }
    },
    
    # ===== 結論 =====
    {
        'object': 'block',
        'type': 'heading_3',
        'heading_3': {
            'rich_text': [{'type': 'text', 'text': {'content': '五、結論'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'callout',
        'callout': {
            'icon': {'type': 'emoji', 'emoji': '⚠️'},
            'rich_text': [{'type': 'text', 'text': {'content': '~/.linkpi/memory.md 記憶檔案內容極度稀疏，僅有 1 筆有效記憶（大寶），且為早期測試記錄。'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '大寶記憶：僅有 model ID 確認與繁體中文偏好設定，無實質工作記憶'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '小寶記憶：全部為空內容錯誤，無任何有效記憶'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': 'Pi Agent 記憶：3 筆全為空內容請求，無實質記憶'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '有效記憶率僅 20%，跨 Agent 記憶共享機制可能未正確運作'}}]
        }
    },
    {
        'object': 'block',
        'type': 'bulleted_list_item',
        'bulleted_list_item': {
            'rich_text': [{'type': 'text', 'text': {'content': '建議：檢查 LinkPi.py 的記憶寫入邏輯，確保每次 conversation 都有實質內容才寫入 memory.md'}}]
        }
    },
    
    {
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{'type': 'text', 'text': {'content': '報告日期：2026-04-30 | 檔案來源：~/.linkpi/memory.md'}}]
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
