import json

file_path = r"C:\Projects\DGTK\DevelopmentFiles\模型訓練記錄\Jupyter\CYG分文\data\CYG1108.json"

# 定義我們建立的「性質規則」
rules = {
    "SA": ["會議", "理監事", "會員", "基金會", "社會福利", "捐贈", "收容", "安置", "志願服務", "社工", "保障", "津貼", "理、監事", "大會"],
    "PW": ["施工", "維護", "巡查", "月報", "日誌", "檢修", "機電", "工地", "材料送審", "計畫", "工程", "施工"],
    "EA": ["驗收", "竣工", "結算", "完成", "履行", "承攬", "估驗", "履約", "驗收完成"],
    "ED": ["教育", "學校", "國中", "國小", "教師", "學生", "教學", "研習", "課程", "學術", "資優", "校長", "教育"],
    "CD": ["建照", "建築", "地號", "土地", "徵收", "設計", "查驗", "缺失補正", "竣工查驗", "建物", "建築師"],
    "TS": ["暫停", "變更", "登記", "勞務採購", "新聞", "媒體", "服務案", "變更登記"],
    "CA": ["判決", "刑事", "法院", "役男", "徵集", "司法", "執行", "扣押", "訴願", "判決", "被告", "答辯"],
    "LA": ["不動產", "經紀", "土地", "徵收", "補償", "地政"],
    "PE": ["退休", "離職", "派免", "聘僱", "人事", "考核", "職務", "薪資", "任職", "調任", "職務"],
    "KT": ["資安", "數位", "系統", "資訊", "數位發展", "AI", "數據", "平台", "軟體"],
    "GA": ["獎勵", "公告", "行政", "核定", "查照", "獎金", "公告", "獎勵檢舉"]
}

# 排除清單
EXCLUDED_LABELS = ["X01", "X02", "X03", "X04", "X05", "X06"]

def analyze_non_x_conflicts():
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    conflicts = []

    for idx, item in enumerate(data):
        text = item.get("text", "")
        label = item.get("label", "")
        reason = item.get("判斷方式", "")
        
        # 跳過 X 開頭的標籤
        if label in EXCLUDED_LABELS:
            continue

        # 檢查邏輯 1: Label 與 Text 內容不符 (性質衝突)
        found_other_labels = []
        for l_name, keywords in rules.items():
            if l_name != label:
                if any(kw in text for kw in keywords):
                    found_other_labels.append(l_name)

        if found_other_labels:
            conflicts.append({
                "index": idx,
                "text": text[:60] + "...",
                "current_label": label,
                "detected_other_labels": found_other_labels,
                "reason_in_file": reason
            })

        # 檢查邏輯 2: 依賴單位 (雖然 label 不是 X，但判斷方式仍顯示邏輯錯誤)
        if "來文機關" in reason or "來文字號" in reason or "來文" in reason:
            conflicts.append({
                "index": idx,
                "text": text[:60] + "...",
                "current_label": label,
                "detected_other_labels": ["邏輯依賴單位"],
                "reason_in_file": reason
            })

    return conflicts

if __name__ == "__main__":
    conflict_list = analyze_non_x_conflicts()
    print(json.dumps(conflict_list, ensure_ascii=False, indent=4))
