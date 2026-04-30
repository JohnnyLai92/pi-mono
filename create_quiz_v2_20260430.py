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

# 找到今天的 heading_2
blocks = notion.blocks.children.list(block_id=page_id)
today_heading_id = None
for b in blocks.get('results', []):
    if b.get('type') == 'heading_2':
        title = b.get('heading_2', {}).get('rich_text', [{}])[0].get('plain_text', '')
        if '2026-04-30' in title:
            today_heading_id = b['id']
            break

if not today_heading_id:
    print('ERROR: Could not find today heading_2')
    exit(1)

print(f'Today heading ID: {today_heading_id}')

# 題目資料
questions = [
    {
        'title': '題目 1：關於深度學習中的梯度消失問題（Vanishing Gradient），下列敘述何者正確？',
        'options': [
            '(A) 梯度消失主要發生在淺層網路，深層網路因層數多反而不易發生',
            '(B) 使用 ReLU 激活函數可以有效緩解梯度消失問題，因為其在正區間的梯度恆為 1',
            '(C) 梯度消失意味著權重更新過快，導致模型收斂速度過快',
            '(D) 梯度消失與激活函數的選擇無關，僅與學習率設定有關'
        ],
        'answer': '我的答案：',
        'result': '批閱結果：',
        'explanation': '✓ 梯度消失主要發生在深層網路中，使用 sigmoid/tanh 時梯度逐層相乘趨近於 0。ReLU 在 x>0 時梯度為 1，有效緩解此問題。B 正確，A/C/D 皆錯。'
    },
    {
        'title': '題目 2：在自然語言處理中，「詞向量（Word Embedding）」的主要特性為何？',
        'options': [
            '(A) 詞向量將每個詞映射為唯一且固定維度的連續向量，語意相近的詞在向量空間中距離較近',
            '(B) 詞向量僅能捕捉詞的拼寫特徵，無法反映語意或語法關係',
            '(C) 詞向量的維度越高，模型的表現一定越好，因此應盡量使用高維向量',
            '(D) 詞向量是離散的稀疏表示，每個詞只有單一非零元素'
        ],
        'answer': '我的答案：',
        'result': '批閱結果：',
        'explanation': '✓ 詞向量將詞映射為連續空間中的固定維度向量，語意相近的詞距離較近（如 king-man+woman≈queen）。A 正確，B/C/D 皆錯（詞向量是密集且能捕捉語意）。'
    },
    {
        'title': '題目 3：關於遷移學習（Transfer Learning）在 AI 實務中的應用，下列何者描述正確？',
        'options': [
            '(A) 遷移學習只能應用於電腦視覺領域，不適用於 NLP 或推薦系統',
            '(B) 遷移學習利用在大型資料集上訓練的模型知識，微調至特定任務以減少訓練時間與資料需求',
            '(C) 遷移學習需要從零開始訓練所有層級，僅改變最後的輸出層',
            '(D) 遷移學習會導致模型過擬合，因此在生產環境中不建議使用'
        ],
        'answer': '我的答案：',
        'result': '批閱結果：',
        'explanation': '✓ 遷移學習利用預訓練模型（如 ImageNet、BERT）的知識，微調至特定任務，減少資料與時間需求。B 正確，A/C/D 皆錯（遷移學習適用於多領域，且可微調部分或全部層級）。'
    },
    {
        'title': '題目 4：在 AI 專案的生命週期中，「資料標註（Data Labeling）」的品質直接影響什麼？',
        'options': [
            '(A) 僅影響模型的訓練速度，與最終準確率無關',
            '(B) 直接影響模型的學習品質與泛化能力，垃圾進垃圾出（Garbage In, Garbage Out）',
            '(C) 標註品質僅在訓練階段重要，部署後不再需要考慮',
            '(D) 標註品質可由自動化工具完全替代，不需要人工審查'
        ],
        'answer': '我的答案：',
        'result': '批閱結果：',
        'explanation': '✓ 資料標註品質直接影響模型學習品質，垃圾進垃圾出（GIGO）是 ML 基本原則。B 正確，A/C/D 皆錯（標註品質影響所有階段，自動化工具仍需人工審查）。'
    },
    {
        'title': '題目 5：關於聯邦學習（Federated Learning）的核心概念，下列敘述何者正確？',
        'options': [
            '(A) 聯邦學習將所有個人資料集中到雲端伺服器進行模型訓練，提升隱私保護',
            '(B) 聯邦學習在分散式裝置上本地訓練模型，僅上傳模型權重更新而非原始資料',
            '(C) 聯邦學習僅適用於非監督式學習，不支援分類或預測任務',
            '(D) 聯邦學習需要所有參與裝置具有相同的硬體規格才能運作'
        ],
        'answer': '我的答案：',
        'result': '批閱結果：',
        'explanation': '✓ 聯邦學習在本地裝置訓練，僅上傳權重更新，保護隱私。B 正確，A/C/D 皆錯（聯邦學習保護隱私而非集中資料，適用於多種任務，硬體不需相同）。'
    },
    {
        'title': '題目 6：在強化學習（Reinforcement Learning）中，「獎勵函數（Reward Function）」的設計對訓練結果有何影響？',
        'options': [
            '(A) 獎勵函數僅影響訓練速度，不影響最終學習的政策（Policy）',
            '(B) 獎勵函數設計不当會導致代理者找到捷徑或誤差行為（Reward Hacking）',
            '(C) 獎勵函數的數值範圍必須固定在 0 到 1 之間，否則模型無法收斂',
            '(D) 強化學習不需要獎勵函數，代理者可自行發現最佳策略'
        ],
        'answer': '我的答案：',
        'result': '批閱結果：',
        'explanation': '✓ 獎勵函數引導代理者行為，設計不當會導致 Reward Hacking（代理者找漏洞獲得高分但非預期行為）。B 正確，A/C/D 皆錯（影響最終政策，數值無固定範圍，需要明確獎勵）。'
    },
    {
        'title': '題目 7：關於 AI 模型的「公平性（Fairness）」評估，以下哪種做法最能確保決策無偏誤？',
        'options': [
            '(A) 只要模型整體準確率高，就不需要特別關注公平性指標',
            '(B) 應使用多個公平性指標（如 Demographic Parity、Equalized Odds）交叉檢視不同群體的表現差異',
            '(C) 公平性僅是倫理問題，與技術實現無關，只需依賴人工審查即可',
            '(D) 一旦模型在訓練階段達公平，部署後就不會產生新的偏誤'
        ],
        'answer': '我的答案：',
        'result': '批閱結果：',
        'explanation': '✓ 公平性需多指標檢視（Demographic Parity、Equalized Odds、Predictive Parity），不同指標可能有衝突。B 正確，A/C/D 皆錯（準確率高不等於公平，公平需持續監控）。'
    },
    {
        'title': '題目 8：在時間序列預測中，「交叉驗證（Cross-Validation）」的正確做法為何？',
        'options': [
            '(A) 應使用隨機 K-Fold 交叉驗證，將資料隨機打亂後分成 K 份',
            '(B) 應使用時間序列特定的交叉驗證（如 TimeSeriesSplit），保留時間順序避免資料外洩',
            '(C) 時間序列資料不適用交叉驗證，因為數據點之間存在相關性',
            '(D) 時間序列交叉驗證時，訓練集應包含未來資料，以提供更多資訊'
        ],
        'answer': '我的答案：',
        'result': '批閱結果：',
        'explanation': '✓ 時間序列資料需保留時間順序，使用 TimeSeriesSplit 避免用未來預測過去（資料外洩）。B 正確，A 錯（隨機 K-Fold 會打亂時間順序），C/D 皆錯。'
    },
    {
        'title': '題目 9：關於 AI 專案中的「數據隱私合規」，GDPR 對個人資料處理有何核心要求？',
        'options': [
            '(A) GDPR 僅適用於歐盟境內企業，國際企業不受其約束',
            '(B) GDPR 要求資料最小化原則、使用者同意、被遺忘權及自動決策的透明度',
            '(C) GDPR 允許企業任意收集個人資料，只要在隱私條款中說明即可',
            '(D) GDPR 不適用於 AI 模型訓練資料，僅限制即時個人資料處理'
        ],
        'answer': '我的答案：',
        'result': '批閱結果：',
        'explanation': '✓ GDPR 要求資料最小化、明確同意、被遺忘權、自動決策透明等。B 正確，A/C/D 皆錯（GDPR 適用於處理歐盟居民資料的國際企業，限制資料收集，涵蓋訓練資料）。'
    },
    {
        'title': '題目 10：在部署 AI 模型時，「線上推理（Online Inference）」與「離線推理（Batch Inference）」的差異為何？',
        'options': [
            '(A) 線上推理適合即時決策場景（如推薦系統、風控），離線推理適合批量處理（如每日報表）',
            '(B) 線上推理的準確率一定高於離線推理，因此應優先採用',
            '(C) 離線推理不需要任何計算資源，僅需儲存空間',
            '(D) 線上推理無法使用模型，僅能使用規則系統'
        ],
        'answer': '我的答案：',
        'result': '批閱結果：',
        'explanation': '✓ 線上推理處理即時請求（低延遲），離線推理處理批量資料（高吞吐）。A 正確，B 錯（準確率與部署方式無關），C/D 皆錯（離線推理仍需計算資源，線上推理可使用模型）。'
    },
]

# 把 heading_4 加到 heading_2 下面，不是 page 下面
all_blocks = []

for q in questions:
    # 1. heading_4 (toggleable)
    all_blocks.append({
        'object': 'block',
        'type': 'heading_4',
        'heading_4': {
            'is_toggleable': True,
            'rich_text': [{'type': 'text', 'text': {'content': q['title']}}]
        }
    })
    
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

# 關鍵：block_id 要傳 heading_2 的 ID，不是 page ID
response = notion.blocks.children.append(block_id=today_heading_id, children=all_blocks)

print(f'Created {len(response["results"])} blocks under heading_2')

# 驗證
children = notion.blocks.children.list(block_id=today_heading_id)
print(f'Verified: heading_2 now has {len(children[\"results\"])} children')
for i, c in enumerate(children['results']):
    print(f'  {i+1}. {c.get(\"type\", \"unknown\")} - {c.get(\"created_time\", \"\")}')