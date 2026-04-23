"""
disk_monitor.py — 每日磁碟使用報告，寄發 [小黃報報] Email

執行方式：
  python scripts/disk_monitor.py
"""
import logging
import os
import sys
from datetime import datetime

import psutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from send_email import send_email

logger = logging.getLogger(__name__)

WARN_THRESHOLD = float(os.getenv("DISK_WARN_THRESHOLD", "80"))  # % 以上視為警告


def _human(num: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if num < 1024.0:
            return f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} PB"


def generate_report() -> None:
    now = datetime.now()
    hostname = os.uname().nodename
    time_str = now.strftime("%Y-%m-%d %H:%M")

    lines = []
    warnings = []

    for part in psutil.disk_partitions(all=False):
        # 跳過虛擬或唯讀掛載點
        if "loop" in part.device or part.fstype in ("squashfs", "tmpfs", "devtmpfs"):
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue

        pct = usage.percent
        icon = "⚠️" if pct >= WARN_THRESHOLD else "✅"
        if pct >= WARN_THRESHOLD:
            warnings.append(f"{part.mountpoint} ({pct:.1f}%)")

        lines.append(
            f"{icon} {part.mountpoint}\n"
            f"   裝置：{part.device}  格式：{part.fstype}\n"
            f"   總容量：{_human(usage.total)}\n"
            f"   已使用：{_human(usage.used)} ({pct:.1f}%)\n"
            f"   剩餘：{_human(usage.free)}"
        )

    status_tag = f"⚠️ {len(warnings)} 項警告" if warnings else "✅ 正常"
    subject = f"[小黃報報] 磁碟使用報告 {now.strftime('%Y-%m-%d')} — {status_tag}"

    sep = "─" * 44
    body = (
        f"══{'═'*42}══\n"
        f"🐶 小黃報報 — 磁碟使用報告\n"
        f"══{'═'*42}══\n"
        f"主機：{hostname}\n"
        f"報告時間：{time_str}\n"
        f"警告閾值：{WARN_THRESHOLD:.0f}%\n\n"
        f"{sep}\n"
        f"{'\\n'.join(lines) if lines else '  無可用磁碟資訊'}\n\n"
        f"{sep}\n"
    )

    if warnings:
        body += "⚠️ 空間不足警告：\n"
        for w in warnings:
            body += f"  • {w}\n"
        body += "\n"

    body += f"{'═'*44}\n此報告由小黃自動產生 🐶\n{'═'*44}\n"

    ok = send_email(subject=subject, body=body)
    if ok:
        logger.info("磁碟報告已寄出：%s", subject)
    else:
        logger.error("磁碟報告寄送失敗")


if __name__ == "__main__":
    import logging as _logging
    from dotenv import load_dotenv
    load_dotenv()
    _logging.basicConfig(level=_logging.INFO, format="%(levelname)s: %(message)s")
    generate_report()
