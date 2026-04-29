import pandas as pd
import json
import os

input_file = r"C:\Projects\DGTK\DevelopmentFiles\模型訓練記錄\Jupyter\CYG分文\data\CYG20260428.xlsx"
output_file = r"C:\Projects\DGTK\DevelopmentFiles\模型訓練記錄\Jupyter\CYG分文\data\CYG20260428.json"

try:
    # 讀取 Excel，因為只有一個 Sheet，讀取第一個即可
    df = pd.read_excel(input_file)
    
    # 將 NaN 轉換為 None (在 JSON 中會變成 null)，避免 json.dumps 報錯
    df = df.where(pd.notnull(df), None)
    
    # 轉換為 Dict 格式 (records 模式適合標準 JSON 列表)
    data_dict = df.to_dict(orient='records')
    
    # 寫入 JSON 檔案
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data_dict, f, ensure_ascii=False, indent=4)
        
    print(f"✅ 轉換成功！")
    print(f"📍 輸出路徑: {output_file}")
    print(f"📊 總筆數: {len(data_dict)}")

except Exception as e:
    print(f"❌ 轉換失敗: {e}")
