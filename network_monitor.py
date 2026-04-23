"""
network_monitor.py — 每小時監控網路流量與連線異常，寄發 [小黃報報] 分析報告

設定（.env）：
  NETWORK_MONITOR_INTERVAL      : 監控間隔分鐘，預設 60
  NETWORK_ANOMALY_TRAFFIC_RATIO : 流量異常倍率閾值（相對於歷史平均），預設 3.0
  NETWORK_ANOMALY_CONN_LIMIT    : 連線總數異常閾值，預設 300
  NETWORK_ANOMALY_SAME_IP_LIMIT : 同一遠端 IP 連線數異常閾值，預設 20
"""

import logging
import os
import socket
import sys
from collections import Counter, deque
from datetime import datetime

import psutil
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))
from send_email import send_email

load_dotenv()

logger = logging.getLogger("pibot.network_monitor")

# ── 設定 ───────────────────────────────────────────────────────────────────────
NETWORK_MONITOR_INTERVAL: int = int(os.getenv("NETWORK_MONITOR_INTERVAL", "60"))
ANOMALY_TRAFFIC_RATIO: float = float(os.getenv("NETWORK_ANOMALY_TRAFFIC_RATIO", "3.0"))
ANOMALY_CONN_LIMIT: int = int(os.getenv("NETWORK_ANOMALY_CONN_LIMIT", "300"))
ANOMALY_SAME_IP_LIMIT: int = int(os.getenv("NETWORK_ANOMALY_SAME_IP_LIMIT", "20"))

# 保留最近 24 筆流量歷史（用於計算平均基線）
_HISTORY_SIZE = 24

# ── 可疑 Port 清單（常見惡意軟體 / 非預期服務）────────────────────────────────
_SUSPICIOUS_PORTS = {
    1080, 3128, 4444, 4445, 5554, 5900, 6667, 6668, 6669,
    8080, 8888, 9001, 9050, 9051, 31337, 65535,
}

# ── 內部狀態 ───────────────────────────────────────────────────────────────────
_prev_bytes_sent: int = 0
_prev_bytes_recv: int = 0
_traffic_history: deque = deque(maxlen=_HISTORY_SIZE)   # 存每小時 (sent, recv) bytes
_first_run: bool = True


def _bytes_to_human(num: int) -> str:
    """將 bytes 轉為易讀格式"""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if num < 1024.0:
            return f"{num:.2f} {unit}"
        num /= 1024.0
    return f"{num:.2f} PB"


def _get_process_info(pid: int) -> str:
    """嘗試取得 PID 的進程名稱與執行路徑"""
    if pid is None or pid == 0:
        return "系統進程/未知"
    try:
        proc = psutil.Process(pid)
        return f"{proc.name()} (PID: {pid}, 路徑: {proc.exe()})"
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return f"未知進程 (PID: {pid})"
    except Exception:
        return f"無法存取 (PID: {pid})"


def _get_local_hostname() -> str:
    try:
        return socket.gethostname()
    except Exception:
        return "未知主機"


def _get_network_connections() -> list[dict]:
    """取得目前所有 TCP/UDP 連線"""
    connections = []
    try:
        for conn in psutil.net_connections(kind="inet"):
            if conn.raddr:
                connections.append({
                    "status": conn.status,
                    "local_ip": conn.laddr.ip if conn.laddr else "",
                    "local_port": conn.laddr.port if conn.laddr else 0,
                    "remote_ip": conn.raddr.ip,
                    "remote_port": conn.raddr.port,
                    "pid": conn.pid,
                })
    except (psutil.AccessDenied, PermissionError) as exc:
        logger.warning("取得連線資訊時權限不足（建議以 sudo 執行）：%s", exc)
    except Exception as exc:
        logger.error("取得連線資訊失敗：%s", exc)
    return connections


def _detect_anomalies(
    sent_delta: int,
    recv_delta: int,
    connections: list[dict],
) -> list[str]:
    """偵測異常，回傳異常描述清單"""
    anomalies = []

    # 各進程活躍連線數（macOS 無法直接取得 per-process bytes，以連線數作代理）
    pid_counter = Counter(c["pid"] for c in connections if c["pid"] is not None)

    def _top_procs_str(counter: Counter, n: int = 3) -> str:
        if not counter:
            return "無法取得進程資訊"
        return "、".join(
            f"{_get_process_info(pid)}（{cnt} 條連線）"
            for pid, cnt in counter.most_common(n)
        )

    # 1. 流量異常（與歷史平均相比）
    if len(_traffic_history) >= 3:
        avg_sent = sum(h[0] for h in _traffic_history) / len(_traffic_history)
        avg_recv = sum(h[1] for h in _traffic_history) / len(_traffic_history)

        if avg_sent > 0 and sent_delta > avg_sent * ANOMALY_TRAFFIC_RATIO:
            anomalies.append(
                f"⚠️ 上傳流量異常：本小時 {_bytes_to_human(sent_delta)}，"
                f"歷史平均 {_bytes_to_human(int(avg_sent))}，"
                f"超出 {sent_delta / avg_sent:.1f} 倍\n"
                f"    🔍 疑似來源進程（依連線數）：{_top_procs_str(pid_counter)}"
            )
        if avg_recv > 0 and recv_delta > avg_recv * ANOMALY_TRAFFIC_RATIO:
            anomalies.append(
                f"⚠️ 下載流量異常：本小時 {_bytes_to_human(recv_delta)}，"
                f"歷史平均 {_bytes_to_human(int(avg_recv))}，"
                f"超出 {recv_delta / avg_recv:.1f} 倍\n"
                f"    🔍 疑似來源進程（依連線數）：{_top_procs_str(pid_counter)}"
            )

    # 2. 總連線數異常
    total_conns = len(connections)
    if total_conns >= ANOMALY_CONN_LIMIT:
        anomalies.append(
            f"⚠️ 連線數過多：目前共 {total_conns} 條連線（閾值：{ANOMALY_CONN_LIMIT}）\n"
            f"    🔍 疑似來源進程（依連線數）：{_top_procs_str(pid_counter)}"
        )

    # 3. 同一遠端 IP 連線數過多
    ip_counter = Counter(c["remote_ip"] for c in connections)
    for ip, count in ip_counter.items():
        if count >= ANOMALY_SAME_IP_LIMIT:
            ip_pid_counter = Counter(
                c["pid"] for c in connections
                if c["remote_ip"] == ip and c["pid"] is not None
            )
            anomalies.append(
                f"⚠️ 單一 IP 連線過多：{ip} 共 {count} 條連線（閾值：{ANOMALY_SAME_IP_LIMIT}）\n"
                f"    🔍 發起進程：{_top_procs_str(ip_pid_counter)}"
            )

    # 4. 可疑 Port 連線
    suspicious_found = []
    for conn in connections:
        rport = conn["remote_port"]
        lport = conn["local_port"]
        if rport in _SUSPICIOUS_PORTS:
            proc_info = _get_process_info(conn["pid"])
            suspicious_found.append(f"遠端 {conn['remote_ip']}:{rport} (由 {proc_info} 發起)")
        elif lport in _SUSPICIOUS_PORTS:
            proc_info = _get_process_info(conn["pid"])
            suspicious_found.append(f"本機 Port {lport} ← {conn['remote_ip']} (進程: {proc_info})")

    if suspicious_found:
        detail = "、".join(suspicious_found[:3])
        if len(suspicious_found) > 3:
            detail += f"… 等共 {len(suspicious_found)} 筆"
        anomalies.append(f"⚠️ 可疑 Port 連線：{detail}")

    return anomalies


def _build_report(
    sent_delta: int,
    recv_delta: int,
    connections: list[dict],
    anomalies: list[str],
    report_time: datetime,
) -> tuple[str, str]:
    """產生報告的 (subject, body)"""
    hostname = _get_local_hostname()
    time_str = report_time.strftime("%Y-%m-%d %H:%M")
    status_tag = "🚨 發現異常" if anomalies else "✅ 正常"

    subject = f"[小黃報報] 網路監控報告 {time_str} — {status_tag}"

    # 連線狀態統計
    status_counter = Counter(c["status"] for c in connections)
    status_summary = "、".join(
        f"{st}: {cnt}" for st, cnt in status_counter.most_common()
    ) or "無連線"

    # 遠端 IP Top 5
    ip_counter = Counter(c["remote_ip"] for c in connections)
    top_ips = "\n".join(
        f"    {ip:40s} {cnt} 條" for ip, cnt in ip_counter.most_common(5)
    ) or "    無"

    # 歷史平均
    if len(_traffic_history) >= 2:
        avg_sent = sum(h[0] for h in _traffic_history) / len(_traffic_history)
        avg_recv = sum(h[1] for h in _traffic_history) / len(_traffic_history)
        avg_line = (
            f"  歷史平均上傳：{_bytes_to_human(int(avg_sent))}\n"
            f"  歷史平均下載：{_bytes_to_human(int(avg_recv))}\n"
            f"  歷史樣本數：{len(_traffic_history)} 筆"
        )
    else:
        avg_line = "  （歷史資料累積中，尚無平均基線）"

    anomaly_section = (
        "\n".join(f"  {a}" for a in anomalies)
        if anomalies
        else "  無異常偵測到 🎉"
    )

    body = f"""══════════════════════════════════════════
🐶 小黃報報 — 網路監控分析報告
══════════════════════════════════════════
主機：{hostname}
報告時間：{time_str}
監控間隔：每 {NETWORK_MONITOR_INTERVAL} 分鐘

──────────────────────────────────────────
📊 本期流量統計
──────────────────────────────────────────
  上傳流量：{_bytes_to_human(sent_delta)}
  下載流量：{_bytes_to_human(recv_delta)}
  總流量：{_bytes_to_human(sent_delta + recv_delta)}

{avg_line}

──────────────────────────────────────────
🔌 連線狀態摘要
──────────────────────────────────────────
  總連線數：{len(connections)} 條
  狀態分佈：{status_summary}

  連線最多的遠端 IP（Top 5）：
{top_ips}

──────────────────────────────────────────
🚨 異常偵測結果
──────────────────────────────────────────
{anomaly_section}

──────────────────────────────────────────
💡 異常閾值設定
──────────────────────────────────────────
  流量異常倍率：歷史平均 × {ANOMALY_TRAFFIC_RATIO}
  總連線數上限：{ANOMALY_CONN_LIMIT} 條
  同一 IP 連線上限：{ANOMALY_SAME_IP_LIMIT} 條
  可疑 Port 清單：{len(_SUSPICIOUS_PORTS)} 個常見惡意/非預期 Port

══════════════════════════════════════════
此報告由小黃自動產生，每 {NETWORK_MONITOR_INTERVAL} 分鐘一次 🐶
══════════════════════════════════════════
"""
    return subject, body


def run_network_monitor() -> None:
    """排程任務：執行網路監控並寄送報告"""
    global _prev_bytes_sent, _prev_bytes_recv, _first_run

    now = datetime.now()
    logger.info("網路監控執行中… (%s)", now.strftime("%Y-%m-%d %H:%M"))

    # 取得目前網路 I/O 統計
    try:
        net_io = psutil.net_io_counters()
        curr_sent = net_io.bytes_sent
        curr_recv = net_io.bytes_recv
    except Exception as exc:
        logger.error("無法取得網路 I/O 統計：%s", exc)
        return

    if _first_run:
        # 第一次執行：記錄初始值，不送報告（沒有 delta 可計算）
        _prev_bytes_sent = curr_sent
        _prev_bytes_recv = curr_recv
        _first_run = False
        logger.info("網路監控初始化完成，下次間隔後開始寄發報告")
        return

    sent_delta = max(0, curr_sent - _prev_bytes_sent)
    recv_delta = max(0, curr_recv - _prev_bytes_recv)
    _prev_bytes_sent = curr_sent
    _prev_bytes_recv = curr_recv

    # 更新歷史紀錄
    _traffic_history.append((sent_delta, recv_delta))

    # 取得連線資訊
    connections = _get_network_connections()

    # 異常偵測
    anomalies = _detect_anomalies(sent_delta, recv_delta, connections)

    if anomalies:
        logger.warning("偵測到 %d 項網路異常：%s", len(anomalies), anomalies)
    else:
        logger.info("網路狀態正常（連線數：%d）", len(connections))

    # 產生並寄送報告
    subject, body = _build_report(sent_delta, recv_delta, connections, anomalies, now)
    ok = send_email(subject=subject, body=body)
    if ok:
        logger.info("網路監控報告已寄出：%s", subject)
    else:
        logger.error("網路監控報告寄送失敗")


# 排程由 pi_scheduler.py 負責，此模組僅提供監控函式
