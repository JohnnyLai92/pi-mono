"""
PicoClaw-compatible email sending module for PiBot.
Usage:
  from send_email import send_email
  send_email(subject="...", body="...")

Run directly to send a quick test email:
  python send_email.py
"""

import logging
import os
import smtplib
import sys
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


def send_email(
    subject: str,
    body: str,
    to: str | None = None,
    from_addr: str | None = None,
    smtp_host: str | None = None,
    smtp_port: int | None = None,
    smtp_user: str | None = None,
    smtp_password: str | None = None,
) -> bool:
    """
    Send a plain-text email via SMTP STARTTLS.
    All parameters fall back to environment variables when omitted.
    Returns True on success, False on any failure.
    """
    smtp_host = smtp_host or os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
    smtp_user = smtp_user or os.getenv("SMTP_USER", "")
    smtp_password = smtp_password or os.getenv("SMTP_PASSWORD", "")
    from_addr = from_addr or os.getenv("EMAIL_FROM", smtp_user)
    to = to or os.getenv("EMAIL_TO", "")

    if not smtp_user or not smtp_password:
        logger.warning("Email skipped: SMTP_USER / SMTP_PASSWORD not configured")
        return False
    if not to:
        logger.warning("Email skipped: EMAIL_TO not configured")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = from_addr
        msg["To"] = to
        msg["Subject"] = Header(subject, "utf-8")
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_addr, [to], msg.as_string())

        logger.info("Email sent to %s | subject: %s", to, subject)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.error("Email send failed: %s", exc)
        return False


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    ok = send_email(
        subject="[小白報報] 測試郵件",
        body="強尼，這是標題更新後的測試信！\n\n現在所有由小白發出的郵件都會以 [小白報報] 開頭了 🐶",
    )
    sys.exit(0 if ok else 1)
