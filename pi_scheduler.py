"""
pi_scheduler.py - 統一的排程中心（於 Mac 端運行）

取代原本分散在各個 Flask request 內的 APScheduler，避免搶鎖與逾時。
1. 若需 pi 內容（如財經新聞）：使用獨立的 PiRpcClient 產生內容，再 POST /push 給 LineBot
2. 若只需推播（如喝水、考試）：定時 POST /trigger/<task> 給 LineBot

新功能：整點報時 (每小時 :00)
  - 發送整點通知
  - 檢查過去 1 小時內有無未執行的排程工作
  - 若有未執行項目，推播詢問是否補執行（使用者回覆後由 app.py 處理）
"""

import os
import time
import logging
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import requests

load_dotenv()

# ── Timezone ───────────────────────────────────────────────────────────────────
TZ = ZoneInfo("Asia/Taipei")

# ── Logging ────────────────────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("pi_scheduler")

# ── Config ─────────────────────────────────────────────────────────────────────
LINEBOT_BASE_URL    = os.getenv("LINEBOT_BASE_URL", "http://127.0.0.1:5000")
SCHEDULER_SECRET    = os.getenv("SCHEDULER_SECRET", "")
CHIME_USER_ID       = os.getenv("WATER_REMINDER_USER_ID", "")

# 排程間隔與時間設定
NETWORK_INTERVAL    = int(os.getenv("NETWORK_MONITOR_INTERVAL", "60"))   # 分鐘
WATER_INTERVAL      = int(os.getenv("WATER_INTERVAL_MINUTES", "90"))      # 分鐘
WATER_SLEEP_START   = int(os.getenv("WATER_SLEEP_START", "23"))
WATER_SLEEP_END     = int(os.getenv("WATER_SLEEP_END", "7"))
CHIME_SLEEP_START   = int(os.getenv("CHIME_SLEEP_START", "22"))           # 報時靜默開始
CHIME_SLEEP_END     = int(os.getenv("CHIME_SLEEP_END", "7"))              # 報時靜默結束

FINANCE_NEWS_HOUR   = int(os.getenv("FINANCE_NEWS_HOUR", "7"))
FINANCE_NEWS_MINUTE = int(os.getenv("FINANCE_NEWS_MINUTE", "30"))
DAILY_REPORT_HOUR   = int(os.getenv("DAILY_REPORT_HOUR", "19"))
DAILY_REPORT_MINUTE = int(os.getenv("DAILY_REPORT_MINUTE", "0"))
ISO_QUIZ_NOON_HOUR  = int(os.getenv("ISO_QUIZ_NOON_HOUR", "12"))
ISO_QUIZ_EVE_HOUR   = int(os.getenv("ISO_QUIZ_EVE_HOUR", "20"))
AI_EXAM_NOON_HOUR   = int(os.getenv("AI_EXAM_NOON_HOUR", "12"))
AI_EXAM_NOON_MIN    = int(os.getenv("AI_EXAM_NOON_MIN", "10"))
AI_EXAM_EVE_HOUR    = int(os.getenv("AI_EXAM_EVE_HOUR", "20"))
AI_EXAM_EVE_MIN     = int(os.getenv("AI_EXAM_EVE_MIN", "10"))

# ── 任務名稱對應顯示標籤 ────────────────────────────────────────────────────────
TASK_LABELS: dict[str, str] = {
    "water":        "💧 喝水提醒",
    "quiz-noon":    "📚 ISO 27001 午間練習題",
    "quiz-eve":     "📚 ISO 27001 晚間練習題",
    "ai-exam-noon": "🤖 AI 考題午間練習",
    "ai-exam-eve":  "🤖 AI 考題晚間練習",
    "report":       "📋 工作確認推播",
    "network":      "🌐 網路監控",
    "news":         "📰 財經新聞",
}

# ── 最後執行時間追蹤（啟動時初始化為 now，避免誤報） ────────────────────────────
_now_init = datetime.now(TZ)
_last_run: dict[str, datetime | None] = {name: _now_init for name in TASK_LABELS}


# ── 工具函式 ───────────────────────────────────────────────────────────────────
def _is_sleep_hour(hour: int, sleep_start: int, sleep_end: int) -> bool:
    """判斷指定小時是否在睡眠靜默區間"""
    if sleep_start > sleep_end:          # 跨午夜，例如 22:00 ~ 07:00
        return hour >= sleep_start or hour < sleep_end
    return sleep_start <= hour < sleep_end


def _trigger_linebot(task: str) -> bool:
    """呼叫 LineBot 的 /trigger/<task> 端點，回傳是否成功"""
    url = f"{LINEBOT_BASE_URL}/trigger/{task}"
    logger.info("Triggering LineBot task: %s", task)
    try:
        resp = requests.post(url, json={"token": SCHEDULER_SECRET}, timeout=10)
        resp.raise_for_status()
        _last_run[task] = datetime.now(TZ)
        logger.info("Task %s triggered successfully.", task)
        return True
    except Exception as e:
        logger.error("Failed to trigger task %s: %s", task, e)
        return False


def _push_linebot(user_id: str, text: str) -> bool:
    """直接將內容 Push 給 LineBot（透過 /push 端點）"""
    url = f"{LINEBOT_BASE_URL}/push"
    try:
        resp = requests.post(url, json={
            "token": SCHEDULER_SECRET,
            "user_id": user_id,
            "text": text,
        }, timeout=10)
        resp.raise_for_status()
        logger.info("Content pushed successfully to %s.", user_id)
        return True
    except Exception as e:
        logger.error("Failed to push content: %s", e)
        return False


def _set_hourly_pending(user_id: str, tasks: list[dict]) -> None:
    """通知 LineBot 有待補執行的任務（使用者回覆後由 app.py 觸發）"""
    url = f"{LINEBOT_BASE_URL}/hourly/pending"
    try:
        resp = requests.post(url, json={
            "token": SCHEDULER_SECRET,
            "user_id": user_id,
            "tasks": tasks,
        }, timeout=10)
        resp.raise_for_status()
        logger.info("Hourly pending set: %d tasks for %s", len(tasks), user_id)
    except Exception as e:
        logger.error("Failed to set hourly pending: %s", e)


# ── 各項排程任務 ───────────────────────────────────────────────────────────────
def task_water():        _trigger_linebot("water")
def task_quiz_noon():    _trigger_linebot("quiz-noon")
def task_quiz_eve():     _trigger_linebot("quiz-eve")
def task_ai_exam_noon(): _trigger_linebot("ai-exam-noon")
def task_ai_exam_eve():  _trigger_linebot("ai-exam-eve")
def task_report():       _trigger_linebot("report")
def task_network():      _trigger_linebot("network")

def task_disk_monitor():
    """Run the daily disk monitor and send email report."""
    try:
        import sys
        import os
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
        from scripts.disk_monitor import generate_report
        generate_report()
    except Exception as e:
        logger.error("Error running disk monitor task: %s", e)

def task_memory_summary():
    """Run the daily memory summarization process."""
    try:
        from memory_summarizer import run_daily_memory_summary
        run_daily_memory_summary()
    except Exception as e:
        logger.error("Error running memory summary task: %s", e)

def task_ai_exam_email():
    """Run the daily AI exam email task."""
    try:
        import sys
        import os
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
        from scripts.send_ai_exam import main as run_ai_exam
        run_ai_exam()
    except Exception as e:
        logger.error("Error running ai_exam_email task: %s", e)


# ── 財經新聞（需要 pi RPC 生成內容） ───────────────────────────────────────────
_pi_client = None

def _get_pi_client():
    global _pi_client
    if _pi_client is None:
        from pi_rpc import PiRpcClient
        cmd_raw = os.getenv("PI_CLI_PATH", "pi")
        cmd = [tok for tok in cmd_raw.split() if not tok.startswith("--")]
        _pi_client = PiRpcClient(base_cmd=cmd, env=os.environ.copy(), timeout=300)
    return _pi_client


def task_finance_news() -> None:
    logger.info("Generating finance news via pi_scheduler...")
    try:
        from finance_news import _build_prompt, FINANCE_NEWS_USER_ID
        if not FINANCE_NEWS_USER_ID:
            logger.warning("FINANCE_NEWS_USER_ID 未設定，略過新聞推播")
            return

        target_date = date.today() - timedelta(days=1)
        prompt = _build_prompt(target_date)

        pi = _get_pi_client()
        logger.info("Asking pi for news summary...")
        result = pi.prompt(prompt)

        date_str = target_date.strftime("%Y/%m/%d")
        header = f"📰 {date_str} 國際財經 10 大新聞\n{'─' * 20}\n\n"
        message = header + result

        if len(message) > 4900:
            message = message[:4880] + "\n\n…（內容過長已截斷）"

        _push_linebot(FINANCE_NEWS_USER_ID, message)
        _last_run["news"] = datetime.now(TZ)
        logger.info("Finance news generated and pushed.")

    except Exception as e:
        logger.error("Error in finance news task: %s", e)


# ── 整點報時：檢查未執行的排程並推播 ──────────────────────────────────────────
def _check_missed_jobs(now: datetime) -> list[dict]:
    """
    檢查過去 1 小時內哪些排程工作未執行。
    回傳格式：[{"task": "water", "label": "💧 喝水提醒", "expected": "13:30"}]
    """
    missed: list[dict] = []
    hour_ago = now - timedelta(hours=1)

    # --- 區間任務（interval）---
    # 網路監控：每 NETWORK_INTERVAL 分鐘，寬限 5 分鐘
    grace_network = 5 * 60
    last = _last_run.get("network")
    if last is None or (now - last).total_seconds() > NETWORK_INTERVAL * 60 + grace_network:
        expected_t = (now - timedelta(minutes=NETWORK_INTERVAL)).strftime("%H:%M")
        missed.append({"task": "network", "label": TASK_LABELS["network"], "expected": expected_t})

    # 喝水提醒：每 WATER_INTERVAL 分鐘，若目前在睡眠時間則略過
    if not _is_sleep_hour(now.hour, WATER_SLEEP_START, WATER_SLEEP_END):
        grace_water = 10 * 60
        last = _last_run.get("water")
        if last is None or (now - last).total_seconds() > WATER_INTERVAL * 60 + grace_water:
            expected_t = (now - timedelta(minutes=WATER_INTERVAL)).strftime("%H:%M")
            missed.append({"task": "water", "label": TASK_LABELS["water"], "expected": expected_t})

    # --- Cron 任務：檢查是否有排程時間落在過去 1 小時內 ---
    cron_jobs = [
        ("news",         FINANCE_NEWS_HOUR,   FINANCE_NEWS_MINUTE),
        ("report",       DAILY_REPORT_HOUR,   DAILY_REPORT_MINUTE),
        ("quiz-noon",    ISO_QUIZ_NOON_HOUR,  0),
        ("quiz-eve",     ISO_QUIZ_EVE_HOUR,   0),
        ("ai-exam-noon", AI_EXAM_NOON_HOUR,   AI_EXAM_NOON_MIN),
        ("ai-exam-eve",  AI_EXAM_EVE_HOUR,    AI_EXAM_EVE_MIN),
    ]

    for task_name, h, m in cron_jobs:
        # 今天的排程時間點（台北時間）
        scheduled = now.replace(hour=h, minute=m, second=0, microsecond=0)
        # 若該時間點落在 [hour_ago, now) 區間內
        if hour_ago <= scheduled < now:
            last = _last_run.get(task_name)
            if last is None or last < scheduled:
                missed.append({
                    "task": task_name,
                    "label": TASK_LABELS[task_name],
                    "expected": scheduled.strftime("%H:%M"),
                })

    return missed


def task_hourly_chime() -> None:
    """整點報時：推播時報 + 檢查過去 1 小時有無未執行的排程工作"""
    now = datetime.now(TZ)
    hour_str = now.strftime("%H:%M")

    if not CHIME_USER_ID:
        logger.warning("CHIME_USER_ID (WATER_REMINDER_USER_ID) 未設定，跳過整點報時")
        return

    # 靜默時間不推播（不打擾睡眠）
    if _is_sleep_hour(now.hour, CHIME_SLEEP_START, CHIME_SLEEP_END):
        logger.info("整點報時靜默中（%s，靜默區間 %02d:00-%02d:00）", hour_str, CHIME_SLEEP_START, CHIME_SLEEP_END)
        return

    missed = _check_missed_jobs(now)

    lines = [f"🕐 {hour_str} 整點報時"]

    if missed:
        lines += [
            "",
            f"⚠️ 過去 1 小時內有 {len(missed)} 項排程未執行：",
            "",
        ]
        for i, job in enumerate(missed, 1):
            lines.append(f"【{i}】{job['label']}（應於 {job['expected']} 執行）")
        lines += [
            "",
            "是否要補執行？",
            "回覆編號（如：1 或 1,2）、「全部」或「略過」",
        ]
        # 通知 LineBot 儲存待回覆狀態
        _set_hourly_pending(CHIME_USER_ID, missed)
    else:
        lines += ["", "✅ 所有排程均正常執行"]

    _push_linebot(CHIME_USER_ID, "\n".join(lines))
    logger.info("整點報時已送出（%s），未執行任務數：%d", hour_str, len(missed))


# ── 主程式 ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("Starting pi_scheduler...")
    scheduler = BackgroundScheduler(timezone="Asia/Taipei")

    # 🌐 網路監控（每 NETWORK_INTERVAL 分鐘）
    scheduler.add_job(task_network, IntervalTrigger(minutes=NETWORK_INTERVAL), name="網路監控")

    # 💧 喝水提醒（每 WATER_INTERVAL 分鐘）
    scheduler.add_job(task_water, IntervalTrigger(minutes=WATER_INTERVAL), name="喝水提醒")

    # 📰 財經新聞（每日 07:30）
    scheduler.add_job(
        task_finance_news,
        CronTrigger(hour=FINANCE_NEWS_HOUR, minute=FINANCE_NEWS_MINUTE),
        name="財經新聞",
    )

    # 💾 磁碟使用報告（每日 10:30）
    scheduler.add_job(
        task_disk_monitor,
        CronTrigger(hour=10, minute=30),
        name="磁碟使用報告",
    )

    # 📋 工作確認（每日 19:00）
    scheduler.add_job(
        task_report,
        CronTrigger(hour=DAILY_REPORT_HOUR, minute=DAILY_REPORT_MINUTE),
        name="工作確認",
    )

    # 🧠 記憶彙整（每日 17:00）
    scheduler.add_job(
        task_memory_summary,
        CronTrigger(hour=17, minute=0),
        name="記憶彙整",
    )

    # ✉️ AI 考題郵件（每日 12:00）
    scheduler.add_job(
        task_ai_exam_email,
        CronTrigger(hour=12, minute=0),
        name="AI 考題郵件",
    )

    # 📚 ISO 27001 練習題（12:00 & 20:00）
    scheduler.add_job(task_quiz_noon, CronTrigger(hour=ISO_QUIZ_NOON_HOUR, minute=0), name="ISO 午間")
    scheduler.add_job(task_quiz_eve,  CronTrigger(hour=ISO_QUIZ_EVE_HOUR,  minute=0), name="ISO 晚間")

    # 🤖 AI 應用規劃師練習題（12:10 & 20:10）
    scheduler.add_job(
        task_ai_exam_email,
        CronTrigger(hour=AI_EXAM_NOON_HOUR, minute=AI_EXAM_NOON_MIN),
        name="AI 午間",
    )
    scheduler.add_job(
        task_ai_exam_email,
        CronTrigger(hour=AI_EXAM_EVE_HOUR, minute=AI_EXAM_EVE_MIN),
        name="AI 晚間",
    )

    # 🕐 整點報時 + 排程健康檢查（每小時 :00，靜默時間除外）
    scheduler.add_job(task_hourly_chime, CronTrigger(minute=0), name="整點報時")

    scheduler.start()
    logger.info(
        "pi_scheduler 已啟動，共 %d 個排程工作",
        len(scheduler.get_jobs()),
    )

    try:
        while True:
            time.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        if _pi_client:
            _pi_client.close()
