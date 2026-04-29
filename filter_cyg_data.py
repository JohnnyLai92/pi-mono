import pandas as pd

# 定義路徑
input_file = r'C:\Projects\DGTK\DevelopmentFiles\模型訓練記錄\Jupyter\CYG分文\data\CYG20251108.xlsx'
output_file = r'C:\Projects\DGTK\DevelopmentFiles\模型訓練記錄\Jupyter\CYG分文\data\CYG20251108_Filtered.xlsx'

try:
    # 讀取 Excel
    df = pd.read_excel(input_file)
    
    # 檢查 DocDesc 欄位是否存在
    if 'DocDesc' not in df.columns:
        print(f"Error: Column 'DocDesc' not found in {input_file}")
        print(f"Available columns: {df.columns.tolist()}")
    else:
        # 過濾包含 "接篆視事" 或 "人才永續" 的資料
        # 使用 str.contains, na=False 處理空值
        mask = df['DocDesc'].str.contains('接篆視事|人才永續', na=False)
        filtered_df = df[mask]
        
        # 儲存為新檔案
        filtered_df.to_excel(output_file, index=False)
        print(f"Successfully filtered {len(filtered_df)} rows. Saved to {output_file}")

except Exception as e:
    print(f"An error occurred: {e}")
