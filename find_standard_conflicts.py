import json
import re

file_a = r"C:\Projects\DGTK\DevelopmentFiles\模型訓練記錄\Jupyter\CYG分文\data\CYG20260428.json"
file_b = r"C:\Projects\DGTK\DevelopmentFiles\模型訓練記錄\Jupyter\CYG分文\data\CYG1108.json"

def extract_rules(data_a):
    rules = []
    for item in data_a:
        judge_way = item.get("判斷方式", "")
        # 提取包含 "主旨：" 的判斷方式，作為標準性質規則
        if "主旨：" in judge_way:
            match = re.search(r"主旨：([^\\n]+)", judge_way)
            if match:
                keyword = match.group(1).strip()
                # 避免過短的關鍵字導致誤判 (例如只有一個字)
                if len(keyword) > 1:
                    rules.append({
                        "keyword": keyword,
                        "target_unit": item.get("實際承辦單位"),
                        "ref_doc_no": item.get("公文文號"),
                        "ref_subject": item.get("主旨"),
                        "ref_agency": item.get("來文機關")
                    })
    return rules

def analyze_conflicts():
    with open(file_a, 'r', encoding='utf-8') as f:
        data_a = json.load(f)
    with open(file_b, 'r', encoding='utf-8') as f:
        data_b = json.load(f)

    rules = extract_rules(data_a)
    conflicts = []

    for idx, b_item in enumerate(data_b):
        b_text = b_item.get("text", "")
        b_label = b_item.get("label", "") # 文件 b 的 label 即為承辦單位
        
        for rule in rules:
            # 如果 b 的文本中包含了 a 定義的標準主旨關鍵字
            if rule["keyword"] in b_text:
                # 比對目前的標籤是否與標準單位不一致
                if b_label != rule["target_unit"]:
                    conflicts.append({
                        "a_doc_no": rule["ref_doc_no"],
                        "a_subject": rule["ref_subject"],
                        "a_agency": rule["ref_agency"],
                        "a_unit": rule["target_unit"],
                        "b_idx": idx,
                        "b_text": b_text,
                        "b_label": b_label
                    })
                    # 命中一條標準規則即記錄衝突並跳出，避免重複
                    break

    return conflicts

if __name__ == "__main__":
    results = analyze_conflicts()
    # 輸出為 JSON 格式以便後續轉換成 Markdown 表格
    print(json.dumps(results, ensure_ascii=False, indent=4))
