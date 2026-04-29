# Windows 排程工作設定指南

## 📋 目標
設定 Windows 排程工作，讓 AI 應用規劃師題型練習管理 Skill 自動執行：
- **每日 8:00**：自動生成新試卷
- **每小時整點**：自動巡檢並批改試卷

## 🔧 方法 1: 使用工作排程器 GUI

### 步驟 1: 建立批次檔

在 `C:\Projects\github\pi-mono\scripts\` 目錄下建立兩個批次檔：

#### 1.1 `generate_daily_quiz.bat`（每日生成試卷）

```batch
@echo off
chcp 65001 >nul
cd /d C:\Projects\github\pi-mono
echo [%date% %time%] 開始執行每日試卷生成...
python packages/mom/src/skills/ai_quiz_scheduler.py --action=generate
echo [%date% %time%] 執行完畢。
```

#### 1.2 `grade_hourly_quiz.bat`（每小時批改試卷）

```batch
@echo off
chcp 65001 >nul
cd /d C:\Projects\github\pi-mono
echo [%date% %time%] 開始執行試卷批改...
python packages/mom/src/skills/ai_quiz_scheduler.py --action=grade
echo [%date% %time%] 執行完畢。
```

### 步驟 2: 開啟工作排程器

1. 按 `Win + R`，輸入 `taskschd.msc`，按 Enter
2. 右鍵點擊「工作排程器程式庫」→「建立基本工作...」

### 步驟 3: 設定每日生成試卷工作

#### 3.1 一般設定
- **名稱**：`AI Quiz - 每日生成試卷`
- **說明**：每天早上 8:00 自動生成 AI 應用規劃師模擬試卷
- **安全性選項**：
  - ☑ 不論使用者是否登入都要執行
  - ☑ 使用最高權限執行

#### 3.2 觸發程式
- **開始執行**：每天
- **開始時間**：08:00:00
- **進階設定**：
  - ☑ 已啟用

#### 3.3 動作
- **動作**：啟動程式
- **程式或指令碼**：`C:\Projects\github\pi-mono\scripts\generate_daily_quiz.bat`
- **起始位置**：`C:\Projects\github\pi-mono`

#### 3.4 條件
- ☑ 只有在電腦使用交流電源時才啟動
- ☐ 只有在下列網路連線可用時才啟動（不勾選）

#### 3.5 設定
- ☑ 如果工作執行時間超過以下時間，停止工作：`1 小時`
- ☑ 如果工作失敗，重新啟動每隔：`5 分鐘`
- ☑ 重新嘗試次數：`3`
- ☑ 工作完成後重新啟動：`不`

### 步驟 4: 設定每小時批改試卷工作

重複步驟 2-3，但使用以下設定：

#### 4.1 一般設定
- **名稱**：`AI Quiz - 每小時批改試卷`
- **說明**：每小時整點自動巡檢並批改 AI 應用規劃師模擬試卷

#### 4.2 觸發程式
- **開始執行**：每天
- **開始時間**：00:00:00（當日午夜）
- **進階設定**：
  - ☑ 已啟用
  - **重複任務間隔**：`1 小時`
  - **持續時間**：`1 日`

#### 4.3 動作
- **動作**：啟動程式
- **程式或指令碼**：`C:\Projects\github\pi-mono\scripts\grade_hourly_quiz.bat`
- **起始位置**：`C:\Projects\github\pi-mono`

### 步驟 5: 測試工作

1. 在工作排程器中找到剛建立的工作
2. 右鍵點擊 →「執行」
3. 查看「最後執行結果」是否為 `0x0`（成功）
4. 檢查 `C:\Projects\github\pi-mono\logs\` 目錄下的執行日誌

## 🔧 方法 2: 使用 schtasks 命令列（快速設定）

### 2.1 建立每日生成試卷工作

以**系統管理員身份**開啟命令提示字元，執行：

```cmd
schtasks /Create /TN "AI Quiz - 每日生成試卷" ^
  /TR "C:\Projects\github\pi-mono\scripts\generate_daily_quiz.bat" ^
  /SC DAILY /ST 08:00 ^
  /RL HIGHEST ^
  /RU SYSTEM ^
  /F
```

### 2.2 建立每小時批改試卷工作

```cmd
schtasks /Create /TN "AI Quiz - 每小時批改試卷" ^
  /TR "C:\Projects\github\pi-mono\scripts\grade_hourly_quiz.bat" ^
  /SC HOURLY /MO 1 ^
  /ST 00:00 ^
  /RL HIGHEST ^
  /RU SYSTEM ^
  /F
```

### 2.3 驗證工作

```cmd
# 列出所有 AI Quiz 相關工作
schtasks /Query /TN "AI Quiz" /FO LIST

# 查看單一工作詳細資訊
schtasks /Query /TN "AI Quiz - 每日生成試卷" /FO LIST /V
```

### 2.4 管理命令

```cmd
# 執行工作（測試用）
schtasks /Run /TN "AI Quiz - 每日生成試卷"

# 停止工作
schtasks /End /TN "AI Quiz - 每小時批改試卷"

# 刪除工作
schtasks /Delete /TN "AI Quiz - 每日生成試卷" /F
```

## 📊 檢視執行歷史

### 方法 1: 工作排程器 GUI

1. 開啟工作排程器
2. 展開「工作排程器程式庫」
3. 點擊 `AI Quiz - 每日生成試卷`
4. 查看下方「歷程記錄」標籤

### 方法 2: 事件檢視器

1. 按 `Win + R`，輸入 `eventvwr.msc`
2. 展開「應用程式和服務服務記錄」→「Microsoft」→「Windows」→「TaskScheduler」
3. 點擊「Operational」
4. 篩選事件來源為 `TaskScheduler`

## 🐛 疑難排解

### 問題 1: 工作執行失敗（錯誤碼 0x1）

**可能原因**：
- Python 路徑未設定
- 環境變數 `.env` 檔案不存在
- 權限不足

**解決方案**：
```cmd
# 1. 確認 Python 路徑
where python

# 2. 修改批次檔，使用絕對路徑
@echo off
chcp 65001 >nul
cd /d C:\Projects\github\pi-mono
"C:\Users\johnny\AppData\Local\Programs\Python\Python311\python.exe" packages/mom/src/skills/ai_quiz_scheduler.py --action=generate
```

### 問題 2: 工作執行但無實際效果

**可能原因**：
- Notion Token 無效
- 網路連線問題
- Notion 頁面權限不足

**解決方案**：
```cmd
# 手動執行並查看輸出
cd C:\Projects\github\pi-mono
python packages/mom/src/skills/ai_quiz_scheduler.py --action=generate --verbose
```

### 問題 3: 中文亂碼

**解決方案**：
在批次檔開頭加入：
```batch
chcp 65001 >nul
```

並確保 Python 腳本中使用：
```python
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

## 📝 日誌記錄

建議在 Python 腳本中加入日誌記錄：

```python
import logging
from pathlib import Path

# 設定日誌
log_dir = Path('C:/Projects/github/pi-mono/logs')
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'ai_quiz.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('AIQuizScheduler')
```

## 🔐 安全性注意事項

1. **服務帳戶**：
   - 使用 `SYSTEM` 帳戶執行時，需確認有權限訪問 Python 和專案目錄
   - 或使用專用服務帳戶，僅授予必要權限

2. **環境變數保護**：
   - `.env` 檔案設定為唯讀（右鍵 → 內容 → 唯讀）
   - 不將 `.env` 提交到 Git

3. **防火牆**：
   - 允許 Python 訪問 Notion API（api.notion.com:443）

## 📞 支援

- **問題回報**：請聯繫強尼（Johnny）
- **文檔更新**：2026-04-27
