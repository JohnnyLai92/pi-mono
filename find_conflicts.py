import json

file_path = r"C:\Projects\DGTK\DevelopmentFiles\模型訓練記錄\Jupyter\CYG分文\data\CYG1108.json"

# 定義我們建立的「性質規則」
# 這裡的 Key 是 Label，Value 是該 Label 應該對應的關鍵字或概念
rules = {
    "SA": ["會議", "理監事", "會員", "基金會", "社會福利", "捐贈", "收容", "安置", "志願服務", "社工", "保障", "津貼"],
    "PW": ["施工", "維護", "巡查", "月報", "日誌", "檢修", "機電", "工地", "維護", "材料送審", "計畫"],
    "EA": ["驗收", "竣工", "結算", "完成", "履行", "承攬", "估驗", "驗收完成"],
    "ED": ["教育", "學校", "國中", "國小", "教師", "學生", "教學", "研習", "課程", "學術", "資優"],
    "CD": ["建照", "建築", "地號", "土地", "徵收", "設計", "查驗", "缺失補正", "竣工查驗"],
    "TS": ["暫停", "變更", "登記", "勞務採購", "新聞", "媒體", "服務案"],
    "CA": ["判決", "刑事", "法院", "役男", "徵集", "司法", "執行", "扣押", "訴願"],
    "LA": ["不動產", "經紀", "土地", "徵收", "補償", "地政"],
    "PE": ["退休", "離職", "派免", "聘僱", "人事", "考核", "職務", "薪資"],
    "KT": ["資安", "數位", "系統", "資訊", "數位發展", "AI", "數據", "平台"],
    "GA": ["獎勵", "公告", "行政", "核定", "查照", "獎金"]
}

def analyze_conflicts():
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    conflicts = []

    for idx, item in enumerate(data):
        text = item.get("text", "")
        label = item.get("label", "")
        reason = item.get("判斷方式", "")
        
        # 檢查邏輯 1: Label 是否與其內容完全無關 (例如內容是人事，Label 卻是工程)
        # 我們用排除法：如果 Label 的關鍵字完全沒出現在 text 中，且 text 裡有強烈的其他 Label 關鍵字
        
        found_other_labels = []
        for l_name, keywords in rules.items():
            if l_name != label:
                if any(kw in text for kw in keywords):
                    found_other_labels.append(l_name)

        # 如果發現 text 裡面有明顯屬於其他標籤的字眼，但 Label 卻是現在這個
        if found_other_labels:
            conflicts.append({
                "index": idx,
                "text": text[:50] + "...",
                "current_label": label,
                "detected_other_labels": found_other_labels,
                "reason_in_file": reason
            })

        # 檢查邏輯 2: 判斷方式是否在「根據單位分類」而非「根據性質分類」
        # 如果判斷方式提到「來文機關」或「來文字號」，這在訓練模型時屬於「特徵洩漏」或「邏輯衝突」
        if "來文機關" in reason or "來文字號" in reason or "來文" in reason:
            conflicts.append({
                "index": idx,
                "text": text[:50] + "...",
                "current_label": label,
                "detected_other_labels": ["邏輯依賴單位"],
                "reason_in_file": reason
            })

    return conflicts

if __name__ == "__main__":
    conflict_list = analyze_conflicts()
    print(json.dumps(conflict_list, ensure_ascii=False, indent=4))
