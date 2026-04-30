import os, json
from dotenv import load_dotenv
from httpx import Client as HTTPClient
from notion_client import Client
import ssl

ssl._create_default_https_context = lambda: ssl._create_unverified_context()

load_dotenv('C:/Projects/github/pi-mono/.env')
token = os.environ['NOTION_TOKEN']

notion = Client(
    options={'auth': token},
    client=HTTPClient(verify=False, headers={'Authorization': f'Bearer {token}'})
)

page_id = '34caad32-6752-8127-a846-eed9a69e0de5'

# 定義每題的結構
questions_data = [
    {
        'title': '題目 1：關於機器學習模型評估指標中，F1-Score 與 AUC-ROC 的差異與適用情境？',
        'options': [
            '(A) F1-Score 適合不平衡資料集，AUC-ROC 適合平衡資料集',
            '(B) F1-Score 是 Precision 與 Recall 的調和平均數，AUC-ROC 反映分類器在不同閾值下的整體表現',
            '(C) F1-Score 只適用於多分類，AUC-ROC 只適用於二分類',
            '(D) AUC-ROC 能反映預測機率的分佈品質，F1-Score 只能反映單一閾值下的表現'
        ],
        'answer': '我的答案：',
        'result': '批閱結果：B、D',
        'explanation': 'F1-Score 是 Precision 與 Recall 的調和平均，對類別不平衡較不敏感。AUC-ROC 綜合考量所有閾值下的 TPR 與 FPR，反映模型排序能力。D 亦正確，AUC-ROC 反映預測機率排序品質，F1 僅限單一閾值。'
    },
    {
        'title': '題目 2：AI 專案中「資料偏誤」（Data Bias）的來源有哪些？如何檢測與緩解？',
        'options': [
            '(A) 資料偏誤僅來自資料收集階段，與後續處理無關',
            '(B) 採樣偏誤、標籤偏誤、歷史偏誤是常見來源，可透過分層抽樣與多樣化資料來源緩解',
            '(C) 只要增加資料量，就能自動消除資料偏誤',
            '(D) 資料偏誤無法量化，只能靠人工經驗判斷'
        ],
        'answer': '我的答案：',
        'result': '批閱結果：B',
        'explanation': '資料偏誤來自多個階段（收集、標籤、歷史），需透過分層抽樣、多樣化來源、公平性指標檢測與緩解。A/C/D 皆錯。'
    },
    {
        'title': '題目 3：在 Transformer 架構中，Multi-Head Attention 的設計原理與優勢為何？',
        'options': [
            '(A) 多個注意力頭共享同一組權重矩陣，降低計算成本',
            '(B) 每個注意力頭獨立學習不同的子空間表示，合併後能同時捕捉短距離與長距離依賴',
            '(C) Multi-Head Attention 僅用於 encoder，decoder 只使用 Single-Head Attention',
            '(D) 增加注意力頭數量必然提升模型效果，無任何限制'
        ],
        'answer': '我的答案：',
        'result': '批閱結果：B',
        'explanation': 'Multi-Head Attention 讓模型在不同子空間中捕捉不同類型的依賴關係。A 錯（各頭有獨立權重），C 錯（decoder 也用），D 錯（過多頭會過擬合）。'
    },
    {
        'title': '題目 4：什麼是「冷啟動問題」？在推薦系統中有哪些常見的解決策略？',
        'options': [
            '(A) 冷啟動指系統訓練完成後效能下降的問題',
            '(B) 冷啟動指新使用者或新物品缺乏互動資料時的推薦困境，可透過內容推薦、熱門推薦或探索-利用策略緩解',
            '(C) 冷啟動只能透過增加訓練資料量來解決',
            '(D) 冷啟動僅影響使用者端，不影響物品端'
        ],
        'answer': '我的答案：',
        'result': '批閱結果：B',
        'explanation': '冷啟動指新使用者或新物品缺乏互動歷史的問題。策略包括：內容基推薦、熱門推薦、探索-利用策略。A/C/D 皆錯。'
    },
    {
        'title': '題目 5：企業資料治理中，Data Catalog 與 Data Lineage 的差異與關聯？',
        'options': [
            '(A) Data Catalog 記錄資料的來源與轉換流程，Data Lineage 提供資料的搜尋與分類',
            '(B) Data Catalog 是資料的目錄與檢索系統，Data Lineage 追蹤資料從來源到終端的完整流向與轉換',
            '(C) Data Catalog 與 Data Lineage 是同一個概念，只是名稱不同',
            '(D) Data Lineage 僅用於視覺化展示，無實際治理功能'
        ],
        'answer': '我的答案：',
        'result': '批閱結果：B',
        'explanation': 'Data Catalog 是目錄與搜尋系統，Data Lineage 追蹤完整流向與轉換路徑。兩者互補。A/C/D 皆錯。'
    },
    {
        'title': '題目 6：LLM 的「幻覺」（Hallucination）現象成因與減少幻覺的技術方法？',
        'options': [
            '(A) 幻覺僅因訓練資料不足所致，增加資料量即可完全消除',
            '(B) 幻覺源自 LLM 學習的是語境機率而非事實，可透過 RAG、Fine-tuning 與 Chain-of-Thought 緩解',
            '(C) 幻覺只在生成對話時出現，在數學計算中不會發生',
            '(D) 提高 Temperature 參數能有效減少幻覺'
        ],
        'answer': '我的答案：',
        'result': '批閱結果：B',
        'explanation': 'LLM 是機率模型，生成最可能文字而非事實。RAG 提供知識來源，Fine-tuning 調整風格，CoT 引導推理。A/C/D 皆錯（高 Temperature 加重幻覺）。'
    },
    {
        'title': '題目 7：AI 專案導入時，如何設計「人機協作」的工作流程以提升效率？',
        'options': [
            '(A) 完全自動化，將所有決策交給 AI，人力僅負責監控',
            '(B) AI 處理高重複性與大量資料分析，人類負責決策判斷、倫理審查與異常處理',
            '(C) 人類應全程介入每個步驟，AI 僅提供輔助建議',
            '(D) 人機協作不需要設計，只要建立 AI 模型即可自然達成'
        ],
        'answer': '我的答案：',
        'result': '批閱結果：B',
        'explanation': 'AI 處理重複性/大量工作，人類保留決策權、倫理審查與異常處理（Human-in-the-loop）。A/C/D 皆錯。'
    },
    {
        'title': '題目 8：梯度下降中，SGD、Mini-batch 與 Batch 的比較與選擇？',
        'options': [
            '(A) Mini-batch 結合 SGD 的快與 Batch 的穩定，是實務上最常見的選擇',
            '(B) Batch Gradient Descent 每次用全部資料更新，適合超大型資料集',
            '(C) SGD 每次僅用一筆資料更新，收斂最慢但最準確',
            '(D) 三種方法在所有情境下表現相同，無差別'
        ],
        'answer': '我的答案：',
        'result': '批閱結果：A',
        'explanation': 'Mini-batch 平衡速度與穩定性，利用 GPU 平行運算。SGD 收斂快但震盪大，Batch 記憶體需求高。B/C/D 皆錯。'
    },
    {
        'title': '題目 9：AI 系統安全中，Adversarial Attack 的原理與防禦機制？',
        'options': [
            '(A) Adversarial Attack 是透過對輸入加入極小擾動，使模型產生錯誤預測',
            '(B) 常見防禦包括敵對訓練、輸入預處理（平滑化）、驗證機制',
            '(C) Adversarial Attack 僅存在於影像分類，不適用於 NLP 或聲音模型',
            '(D) 完全防禦 Adversarial Attack 需犧牲所有模型效能'
        ],
        'answer': '我的答案：',
        'result': '批閱結果：A、B',
        'explanation': '微擾使人眼無法察覺但模型誤判。敵對訓練、輸入平滑化、檢測機制都是有效防禦。C/D 皆錯。'
    },
    {
        'title': '題目 10：如何評估 AI 專案的 Business Value？請列出至少五個可衡量的指標。',
        'options': [
            '(A) 需多維度評估：ROI、處理時間縮短、錯誤率降低、客戶滿意度提升、人力成本節省',
            '(B) AI 專案的 Business Value 僅能以技術指標評估（如準確率、F1-Score）',
            '(C) 只要計算了 ROI，就無需追蹤其他非財務指標',
            '(D) Business Value 的評估只需考慮短期財務回報，不需考量長期戰略'
        ],
        'answer': '我的答案：',
        'result': '批閱結果：A',
        'explanation': '需多維度評估：ROI、時間、品質、客戶滿意度、創新力等。B/C/D 皆錯，需綜合財務與非財務指標，考量長期戰略。'
    },
]

all_blocks = []

for q in questions_data:
    # 1. heading_4 (toggleable)
    heading_block = {
        'object': 'block',
        'type': 'heading_4',
        'heading_4': {
            'is_toggleable': True,
            'rich_text': [{'type': 'text', 'text': {'content': q['title']}}]
        }
    }
    all_blocks.append(heading_block)
    
    # 2. bulleted_list_item (4 options)
    for opt in q['options']:
        all_blocks.append({
            'object': 'block',
            'type': 'bulleted_list_item',
            'bulleted_list_item': {
                'rich_text': [{'type': 'text', 'text': {'content': opt}}]
            }
        })
    
    # 3. callout - my answer
    all_blocks.append({
        'object': 'block',
        'type': 'callout',
        'callout': {
            'rich_text': [{'type': 'text', 'text': {'content': q['answer']}}]
        }
    })
    
    # 4. callout - result + explanation
    callout_text = q['result'] + '\n\n解析：' + q['explanation']
    all_blocks.append({
        'object': 'block',
        'type': 'callout',
        'callout': {
            'rich_text': [{'type': 'text', 'text': {'content': callout_text}}]
        }
    })

response = notion.blocks.children.append(block_id=page_id, children=all_blocks)

print(f'Created {len(response["results"])} blocks')
print('Done!')
