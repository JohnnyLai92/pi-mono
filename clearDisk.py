import os                                                                                                                                                                                                                  
import time                                                                                                                                                                                                             
from pathlib import Path                                                                                                                                                                                                

# 設定設定                                                                                                                                                                                                              
TARGET_DIR = r'C:\Users\Johnny'                                                                                                                                                                           
SIZE_THRESHOLD_MB = 100  # 只列出大於 100MB 的檔案                                                                                                                                                                      
AGE_THRESHOLD_DAYS = 180  # 超過 180 天 (約 6 個月)                                                                                                                                                                     

def get_size_format(b, factor=1024, suffix="B"):                                                                                                                                                                        
    """
    將 bytes 轉換為易讀的格式 (MB, GB)
    """
    for unit in ["", "K", "M", "G", "T", "P"]:                                                                                                                                                                          
        if b < factor:                                                                                                                                                                                                  
            return f"{b:.2f}{unit}{suffix}"                                                                                                                                                                             
        b /= factor                                                                                                                                                                                                     

def analyze_appdata():                                                                                                                                                                                                  
    print(f"正在分析: {TARGET_DIR}")                                                                                                                                                                                    
    print(f"篩選條件: 大於 {SIZE_THRESHOLD_MB}MB 且超過 {AGE_THRESHOLD_DAYS} 天未更新\n")                                                                                                                               

    now = time.time()                                                                                                                                                                                                   
    seconds_in_day = 86400                                                                                                                                                                                              

    report = []                                                                                                                                                                                                         
    total_reclaimable_size = 0                                                                                                                                                                                          

    # 使用 os.walk 遍歷目錄                                                                                                                                                                                             
    for root, dirs, files in os.walk(TARGET_DIR):                                                                                                                                                                       
        for name in files:                                                                                                                                                                                              
            file_path = os.path.join(root, name)                                                                                                                                                                        
            try:                                                                                                                                                                                                        
                # 取得檔案狀態                                                                                                                                                                                          
                stat = os.stat(file_path)                                                                                                                                                                               
                file_size = stat.st_size                                                                                                                                                                                
                last_access = stat.st_atime  # 最後存取時間                                                                                                                                                             
                last_mod = stat.st_mtime    # 最後修改時間                                                                                                                                                              

                # 判斷是否符合大小與時間條件 (取存取與修改時間較晚者作為「活躍」指標)                                                                                                                                   
                last_active = max(last_access, last_mod)                                                                                                                                                                
                age_days = (now - last_active) / seconds_in_day                                                                                                                                                         

                if file_size > (SIZE_THRESHOLD_MB * 1024 * 1024) and age_days > AGE_THRESHOLD_DAYS:                                                                                                                     
                    size_str = get_size_format(file_size)                                                                                                                                                               
                    report.append({                                                                                                                                                                                     
                        'path': file_path,                                                                                                                                                                              
                        'size': size_str,                                                                                                                                                                               
                        'age': int(age_days),                                                                                                                                                                           
                        'raw_size': file_size                                                                                                                                                                           
                    })
                    total_reclaimable_size += file_size                                                                                                                                                                 

            except (PermissionError, OSError):                                                                                                                                                                          
                # 忽略系統鎖定或無權限存取的檔案                                                                                                                                                                        
                continue

    # 輸出報告                                                                                                                                                                                                          
    if not report:                                                                                                                                                                                                      
        print("✅ 沒發現符合條件的大型陳舊檔案！你的電腦很乾淨喔。")                                                                                                                                                    
    else:                                                                                                                                                                                                               
        print(f"{'檔案路徑':<80} | {'大小':<10} | {'天數':<5}")                                                                                                                                                         
        print("-" * 100)                                                                                                                                                                                                
        # 按大小排序，從大到小                                                                                                                                                                                          
        report.sort(key=lambda x: x['raw_size'], reverse=True)                                                                                                                                                          

        for item in report:                                                                                                                                                                                             
            print(f"{item['path'][:77]+'...':<80} | {item['size']:<10} | {item['age']} 天")                                                                                                                             

        print("-" * 100)                                                                                                                                                                                                
        print(f"總計可能釋放空間: {get_size_format(total_reclaimable_size)}")                                                                                                                                           
        print("\n⚠️  小白的溫馨提醒：")                                                                                                                                                                                  
        print("1. 在刪除任何檔案前，請務必確認該路徑不是你正在使用的軟體資料夾。")                                                                                                                                      
        print("2. 建議先將檔案移至「回收站」而非直接永久刪除。")                                                                                                                                                        
        print("3. 對於資料夾層級的檢查，建議手動確認該軟體是否已卸載。")                                                                                                                                                

if __name__ == "__main__":                                                                                                                                                                                              
    analyze_appdata()   