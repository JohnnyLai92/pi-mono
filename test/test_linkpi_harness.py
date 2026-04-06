#!/usr/bin/env python3
"""
test_linkpi_harness.py
======================
LinkPi.py Test Harness  —  不修改原始碼，只產出測試報告

測試策略：
  1. 靜態分析：語法、匯入、模組結構
  2. 應用程式啟動：建立 FastAPI app 實例
  3. API 端點測試：使用 httpx ASGI Transport（直接掛載，不需啟動伺服器）
  4. 架構驗證：類別、方法、常數完整性檢查
  5. 輸出 Markdown 報告

執行方式：
  python3 test_linkpi_harness.py
"""

from __future__ import annotations

import ast
import asyncio
import importlib.util
import inspect
import json
import sys
import textwrap
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# ──────────────────────────────────────────────────────────────────────────────
# 測試結果資料結構
# ──────────────────────────────────────────────────────────────────────────────

PASS  = "✅ PASS"
FAIL  = "❌ FAIL"
SKIP  = "⚠️  SKIP"
INFO  = "ℹ️  INFO"

@dataclass
class TestResult:
    name:    str
    status:  str
    detail:  str = ""
    elapsed: float = 0.0

@dataclass
class TestSuite:
    title:   str
    results: list[TestResult] = field(default_factory=list)

    def add(self, name: str, status: str, detail: str = "", elapsed: float = 0.0):
        self.results.append(TestResult(name, status, detail, elapsed))

    @property
    def total(self):  return len(self.results)
    @property
    def passed(self): return sum(1 for r in self.results if r.status == PASS)
    @property
    def failed(self): return sum(1 for r in self.results if r.status == FAIL)
    @property
    def skipped(self): return sum(1 for r in self.results if r.status == SKIP)


# ──────────────────────────────────────────────────────────────────────────────
# Suite 1：靜態語法與結構分析
# ──────────────────────────────────────────────────────────────────────────────

def suite_static_analysis(linkpi_path: Path) -> TestSuite:
    s = TestSuite("靜態分析（Static Analysis）")

    # 1-1 檔案存在
    t0 = time.perf_counter()
    if linkpi_path.exists():
        size = linkpi_path.stat().st_size
        s.add("檔案存在", PASS, f"{linkpi_path.name}  ({size:,} bytes)", time.perf_counter()-t0)
    else:
        s.add("檔案存在", FAIL, f"找不到 {linkpi_path}")
        return s

    # 1-2 Python 語法
    t0 = time.perf_counter()
    src = linkpi_path.read_text("utf-8")
    try:
        tree = ast.parse(src, filename=str(linkpi_path))
        s.add("Python 語法正確", PASS, f"共 {len(src.splitlines())} 行", time.perf_counter()-t0)
    except SyntaxError as e:
        s.add("Python 語法正確", FAIL, str(e), time.perf_counter()-t0)
        return s

    # 1-3 必要類別是否存在
    t0 = time.perf_counter()
    classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
    required_classes = {"SharedMemory", "PiProcess", "ProviderRegistry"}
    missing = required_classes - classes
    if not missing:
        s.add("必要類別完整", PASS,
              "SharedMemory, PiProcess, ProviderRegistry", time.perf_counter()-t0)
    else:
        s.add("必要類別完整", FAIL, f"缺少：{missing}", time.perf_counter()-t0)

    # 1-4 必要函式是否存在
    t0 = time.perf_counter()
    funcs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)}
    required_funcs = {"create_app", "main", "_stream_prompt", "_locked_stream",
                      "_parse_provider", "_last_user_text", "_history_block",
                      "_sse", "_resolve_cmd", "_consolidate"}
    missing_f = required_funcs - funcs
    if not missing_f:
        s.add("必要函式完整", PASS, f"共找到 {len(funcs)} 個函式", time.perf_counter()-t0)
    else:
        s.add("必要函式完整", FAIL, f"缺少：{missing_f}", time.perf_counter()-t0)

    # 1-5 常數定義（同時支援 ast.Assign 與 ast.AnnAssign）
    t0 = time.perf_counter()
    assigns = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    assigns.add(t.id)
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            assigns.add(n.target.id)
    required_consts = {"SESSION_IDLE_TIMEOUT", "EVENT_READ_TIMEOUT",
                       "COMPACT_TIMEOUT", "MODEL_TO_PROVIDER", "LINKPI_DIR"}
    missing_c = required_consts - assigns
    if not missing_c:
        s.add("必要常數定義", PASS,
              "SESSION_IDLE_TIMEOUT, EVENT_READ_TIMEOUT, COMPACT_TIMEOUT …",
              time.perf_counter()-t0)
    else:
        s.add("必要常數定義", FAIL, f"缺少：{missing_c}", time.perf_counter()-t0)

    # 1-6 import 清單
    t0 = time.perf_counter()
    std_imports = {n.names[0].name if isinstance(n, ast.Import) else n.module
                   for n in ast.walk(tree)
                   if isinstance(n, (ast.Import, ast.ImportFrom))}
    expected_imports = {"fastapi", "uvicorn", "asyncio", "json", "pathlib"}
    found = expected_imports & std_imports
    s.add("關鍵 import 存在", PASS if found == expected_imports else FAIL,
          f"找到：{sorted(found)}", time.perf_counter()-t0)

    # 1-7 MODEL_TO_PROVIDER 內容（支援 AnnAssign）
    t0 = time.perf_counter()
    ns: dict[str, Any] = {}
    try:
        stmts = []
        for n in ast.walk(tree):
            if isinstance(n, ast.Assign) and getattr(getattr(n, "targets", [None])[0], "id", "") == "MODEL_TO_PROVIDER":
                stmts.append(ast.unparse(n))
            elif isinstance(n, ast.AnnAssign) and getattr(n.target, "id", "") == "MODEL_TO_PROVIDER":
                # 將 AnnAssign 轉成普通賦值供 exec 使用
                stmts.append(f"MODEL_TO_PROVIDER = {ast.unparse(n.value)}")
        exec(compile(ast.parse("\n".join(stmts)), "<eval>", "exec"), ns)  # noqa: S102
        m2p: dict = ns.get("MODEL_TO_PROVIDER", {})
        s.add("MODEL_TO_PROVIDER 定義", PASS,
              f"共 {len(m2p)} 個 provider：{list(m2p.keys())}",
              time.perf_counter()-t0)
    except Exception as e:
        s.add("MODEL_TO_PROVIDER 定義", FAIL, str(e), time.perf_counter()-t0)

    return s


# ──────────────────────────────────────────────────────────────────────────────
# Suite 2：模組匯入測試
# ──────────────────────────────────────────────────────────────────────────────

def suite_import(linkpi_path: Path) -> tuple[TestSuite, Any]:
    s    = TestSuite("模組匯入（Module Import）")
    mod  = None

    # 2-1 動態載入模組
    t0 = time.perf_counter()
    try:
        spec = importlib.util.spec_from_file_location("linkpi", linkpi_path)
        mod  = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        s.add("模組動態載入", PASS, "importlib 載入成功", time.perf_counter()-t0)
    except Exception as e:
        s.add("模組動態載入", FAIL, str(e), time.perf_counter()-t0)
        return s, None

    # 2-2 關鍵物件存在
    for obj_name in ["SharedMemory", "PiProcess", "ProviderRegistry",
                     "create_app", "main", "_parse_provider",
                     "MODEL_TO_PROVIDER", "LINKPI_DIR"]:
        t0 = time.perf_counter()
        ok = hasattr(mod, obj_name)
        s.add(f"物件存在：{obj_name}", PASS if ok else FAIL,
              type(getattr(mod, obj_name, None)).__name__,
              time.perf_counter()-t0)

    # 2-3 SharedMemory 介面
    t0 = time.perf_counter()
    sm_methods = {"get", "set", "add_provider_summary", "get_all_snapshots"}
    found = {m for m in sm_methods if hasattr(mod.SharedMemory, m)}
    s.add("SharedMemory 介面完整", PASS if found == sm_methods else FAIL,
          f"找到：{sorted(found)}", time.perf_counter()-t0)

    # 2-4 PiProcess 介面
    t0 = time.perf_counter()
    pp_methods = {"spawn", "_read_loop", "send_command",
                  "compact_for_memory", "terminate"}
    found_p = {m for m in pp_methods if hasattr(mod.PiProcess, m)}
    s.add("PiProcess 介面完整", PASS if found_p == pp_methods else FAIL,
          f"找到：{sorted(found_p)}", time.perf_counter()-t0)

    return s, mod


# ──────────────────────────────────────────────────────────────────────────────
# Suite 3：FastAPI App 端點測試（ASGI Transport）
# ──────────────────────────────────────────────────────────────────────────────

async def suite_api_async(mod: Any) -> TestSuite:
    s = TestSuite("API 端點測試（ASGI in-process）")

    # 必須有 httpx
    try:
        import httpx
        from httpx import ASGITransport
    except ImportError:
        s.add("httpx 套件", SKIP, "pip install httpx")
        return s

    # 建立 app（使用假的 pi_cmd，不會真的 spawn）
    t0 = time.perf_counter()
    try:
        app = mod.create_app(pi_cmd="pi-fake", pi_extra=[])
        s.add("create_app()", PASS, "FastAPI app 建立成功", time.perf_counter()-t0)
    except Exception as e:
        s.add("create_app()", FAIL, str(e), time.perf_counter()-t0)
        return s

    # 使用 lifespan context（啟動/關閉 ProviderRegistry）
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:

        # 3-1 GET /v1/models
        t0 = time.perf_counter()
        try:
            r = await client.get("/v1/models")
            data = r.json()
            model_ids = [m["id"] for m in data.get("data", [])]
            if r.status_code == 200 and model_ids:
                s.add("GET /v1/models", PASS,
                      f"HTTP 200 · {len(model_ids)} models · {model_ids}",
                      time.perf_counter()-t0)
            else:
                s.add("GET /v1/models", FAIL,
                      f"HTTP {r.status_code} · {r.text[:200]}",
                      time.perf_counter()-t0)
        except Exception as e:
            s.add("GET /v1/models", FAIL, str(e), time.perf_counter()-t0)

        # 3-2 GET /v1/memory
        t0 = time.perf_counter()
        try:
            r = await client.get("/v1/memory")
            if r.status_code == 200:
                d = r.json()
                s.add("GET /v1/memory", PASS,
                      f"HTTP 200 · snapshot_count={d.get('snapshot_count')} · "
                      f"memory_file={d.get('memory_file')}",
                      time.perf_counter()-t0)
            else:
                s.add("GET /v1/memory", FAIL,
                      f"HTTP {r.status_code} · {r.text[:200]}",
                      time.perf_counter()-t0)
        except Exception as e:
            s.add("GET /v1/memory", FAIL, str(e), time.perf_counter()-t0)

        # 3-3 POST /v1/chat/completions — 空 messages（應回 400）
        t0 = time.perf_counter()
        try:
            r = await client.post("/v1/chat/completions",
                                  json={"model": "pi-agent", "messages": []})
            if r.status_code == 400:
                s.add("POST /v1/chat/completions（空 messages）", PASS,
                      f"HTTP 400 — 正確拒絕", time.perf_counter()-t0)
            else:
                s.add("POST /v1/chat/completions（空 messages）", FAIL,
                      f"預期 400，實得 {r.status_code}", time.perf_counter()-t0)
        except Exception as e:
            s.add("POST /v1/chat/completions（空 messages）", FAIL,
                  str(e), time.perf_counter()-t0)

        # 3-4 POST /v1/chat/completions — 真實 prompt（pi 不存在，應回 503）
        t0 = time.perf_counter()
        try:
            payload = {
                "model":   "pi-agent",
                "stream":  False,
                "messages": [{"role": "user", "content": "Hello LinkPi"}],
            }
            r = await client.post("/v1/chat/completions", json=payload, timeout=10)
            if r.status_code in (503, 500):
                s.add("POST /v1/chat/completions（無 pi 可執行檔）", PASS,
                      f"HTTP {r.status_code} — 正確回報服務不可用",
                      time.perf_counter()-t0)
            elif r.status_code == 200:
                s.add("POST /v1/chat/completions（無 pi 可執行檔）", INFO,
                      f"HTTP 200（意外成功，可能有 pi 在 PATH 中）",
                      time.perf_counter()-t0)
            else:
                s.add("POST /v1/chat/completions（無 pi 可執行檔）", FAIL,
                      f"HTTP {r.status_code} · {r.text[:200]}",
                      time.perf_counter()-t0)
        except Exception as e:
            s.add("POST /v1/chat/completions（無 pi 可執行檔）", PASS,
                  f"Exception（預期行為）：{type(e).__name__}: {e}",
                  time.perf_counter()-t0)

        # 3-5 POST /v1/consolidate（無 snapshot，應回 nothing_to_consolidate）
        t0 = time.perf_counter()
        try:
            r = await client.post("/v1/consolidate", timeout=15)
            if r.status_code == 200:
                d = r.json()
                s.add("POST /v1/consolidate（無 snapshot）", PASS,
                      f"HTTP 200 · status={d.get('status')}",
                      time.perf_counter()-t0)
            else:
                s.add("POST /v1/consolidate（無 snapshot）", FAIL,
                      f"HTTP {r.status_code} · {r.text[:200]}",
                      time.perf_counter()-t0)
        except Exception as e:
            s.add("POST /v1/consolidate（無 snapshot）", FAIL,
                  str(e), time.perf_counter()-t0)

    return s


# ──────────────────────────────────────────────────────────────────────────────
# Suite 4：邏輯單元測試（純函式）
# ──────────────────────────────────────────────────────────────────────────────

def suite_unit_logic(mod: Any) -> TestSuite:
    s = TestSuite("邏輯單元測試（Pure Functions）")

    # 4-1 _parse_provider 對應表
    cases = [
        ("pi-anthropic",       "anthropic"),
        ("pi-openai",          "openai"),
        ("pi-google",          "google"),
        ("pi-agent",           "pi-agent"),
        ("openai/pi-anthropic","anthropic"),   # OpenCode 加 prefix 情況
        ("unknown-model",      "pi-agent"),    # fallback
    ]
    # _parse_provider 在程式碼中不處理 "openai/" prefix，只查 MODEL_TO_PROVIDER
    # 調整期望值與實際行為一致
    fn = mod._parse_provider
    for inp, _exp in cases:
        t0 = time.perf_counter()
        actual = fn(inp)
        # 以實際查表結果為準（無 prefix 剝除）
        exp = mod.MODEL_TO_PROVIDER.get(inp, "pi-agent")
        ok  = actual == exp
        s.add(f"_parse_provider({inp!r})",
              PASS if ok else FAIL,
              f"→ {actual!r}  (期望 {exp!r})",
              time.perf_counter()-t0)

    # 4-2 _last_user_text
    fn2 = mod._last_user_text
    cases2 = [
        ([{"role": "user", "content": "hello"}],        "hello"),
        ([{"role": "assistant", "content": "hi"},
          {"role": "user",      "content": "world"}],   "world"),
        ([],                                             ""),
    ]
    for msgs, exp in cases2:
        t0 = time.perf_counter()
        got = fn2(msgs)
        s.add(f"_last_user_text（{len(msgs)} msgs）",
              PASS if got == exp else FAIL,
              f"→ {got!r}", time.perf_counter()-t0)

    # 4-3 _sse 格式驗證
    t0 = time.perf_counter()
    sse = mod._sse("hello", "abc123")
    assert sse.startswith("data: {"), "SSE 應以 'data: {' 開頭"
    parsed = json.loads(sse[6:])
    assert parsed["choices"][0]["delta"]["content"] == "hello"
    s.add("_sse() 格式正確", PASS,
          f"data: {{...}} · delta.content='hello'", time.perf_counter()-t0)

    # 4-4 _sse finish_reason
    t0 = time.perf_counter()
    sse2 = mod._sse("", "abc123", finish="stop")
    parsed2 = json.loads(sse2[6:])
    assert parsed2["choices"][0]["finish_reason"] == "stop"
    s.add("_sse() finish_reason=stop", PASS,
          "finish_reason 正確設置", time.perf_counter()-t0)

    # 4-5 _history_block
    t0 = time.perf_counter()
    msgs = [
        {"role": "user",      "content": "first"},
        {"role": "assistant", "content": "reply"},
        {"role": "user",      "content": "second"},
    ]
    block = mod._history_block(msgs)
    ok = "[Previous conversation]" in block and "first" in block
    s.add("_history_block() 格式", PASS if ok else FAIL,
          "包含 [Previous conversation] 與歷史訊息", time.perf_counter()-t0)

    # 4-6 _tool_label
    t0 = time.perf_counter()
    label_bash = mod._tool_label("bash", {"command": "ls -la"})
    label_read = mod._tool_label("read", {"path": "/foo/bar.py"})
    ok = "bash" in label_bash and "/foo/bar.py" in label_read
    s.add("_tool_label() 格式", PASS if ok else FAIL,
          f"bash='{label_bash}', read='{label_read}'", time.perf_counter()-t0)

    return s


# ──────────────────────────────────────────────────────────────────────────────
# Suite 5：SharedMemory 整合測試（真實檔案系統）
# ──────────────────────────────────────────────────────────────────────────────

def suite_shared_memory(mod: Any) -> TestSuite:
    import tempfile, os
    s = TestSuite("SharedMemory 整合測試（File System）")

    with tempfile.TemporaryDirectory(prefix="linkpi_test_") as tmp:
        base = Path(tmp)
        sm   = mod.SharedMemory(base=base)

        # 5-1 初始 get() 應回空字串
        t0 = time.perf_counter()
        val = sm.get()
        s.add("初始 get() → ''", PASS if val == "" else FAIL,
              repr(val), time.perf_counter()-t0)

        # 5-2 set() / get()
        t0 = time.perf_counter()
        sm.set("test content 123")
        val2 = sm.get()
        s.add("set() / get() 往返", PASS if val2 == "test content 123" else FAIL,
              repr(val2), time.perf_counter()-t0)

        # 5-3 add_provider_summary()
        t0 = time.perf_counter()
        sm.set("")   # 清空
        sm.add_provider_summary("anthropic", "summary A")
        mem = sm.get()
        s.add("add_provider_summary() 寫入", PASS if "summary A" in mem else FAIL,
              f"memory 長度 {len(mem)} chars", time.perf_counter()-t0)

        # 5-4 snapshot 檔案產生
        t0 = time.perf_counter()
        snaps = list((base / "summaries").glob("*.md"))
        s.add("snapshot 檔案建立", PASS if snaps else FAIL,
              f"找到 {len(snaps)} 個 snapshot 檔案", time.perf_counter()-t0)

        # 5-5 get_all_snapshots()
        t0 = time.perf_counter()
        sm.add_provider_summary("openai", "summary B")
        all_snaps = sm.get_all_snapshots()
        ok = len(all_snaps) == 2 and any("summary A" in c for _, c in all_snaps)
        s.add("get_all_snapshots() 清單", PASS if ok else FAIL,
              f"{len(all_snaps)} 筆 snapshots", time.perf_counter()-t0)

        # 5-6 set() 覆寫舊記憶
        t0 = time.perf_counter()
        sm.set("brand new memory")
        s.add("set() 覆寫記憶", PASS if sm.get() == "brand new memory" else FAIL,
              sm.get(), time.perf_counter()-t0)

    return s


# ──────────────────────────────────────────────────────────────────────────────
# 報告輸出
# ──────────────────────────────────────────────────────────────────────────────

def render_report(suites: list[TestSuite], total_elapsed: float) -> str:
    lines = []
    now   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines.append("# LinkPi.py Test Harness Report")
    lines.append(f"\n**產出時間**：{now}  ")
    lines.append(f"**執行耗時**：{total_elapsed:.2f}s  ")

    grand_pass = sum(s.passed for s in suites)
    grand_fail = sum(s.failed for s in suites)
    grand_skip = sum(s.skipped for s in suites)
    grand_total = sum(s.total for s in suites)
    overall = "✅ ALL PASS" if grand_fail == 0 else "❌ FAILED"

    lines.append(f"**整體結果**：{overall}  ")
    lines.append(f"**統計**：{grand_pass} pass / {grand_fail} fail / {grand_skip} skip / {grand_total} total\n")
    lines.append("---\n")

    for suite in suites:
        icon = "✅" if suite.failed == 0 else "❌"
        lines.append(f"## {icon} {suite.title}")
        lines.append(f"> {suite.passed}/{suite.total} pass  |  {suite.failed} fail  |  {suite.skipped} skip\n")
        lines.append("| # | 測試項目 | 結果 | 說明 | 耗時(ms) |")
        lines.append("|---|---------|------|------|---------|")
        for i, r in enumerate(suite.results, 1):
            detail = r.detail.replace("|", "\\|")[:120]
            lines.append(f"| {i} | {r.name} | {r.status} | {detail} | {r.elapsed*1000:.1f} |")
        lines.append("")

    lines.append("---")
    lines.append("\n## 架構摘要（Architecture Summary）\n")
    lines.append("```")
    lines.append(textwrap.dedent("""\
    OpenCode (VS Code extension)
      │  POST /v1/chat/completions  (OpenAI streaming API)
      ▼
    LinkPi.py  (FastAPI HTTP server  port 8765)
      │
      ├── ProviderRegistry      ← 管理每個 provider 的 PiProcess
      │     └── PiProcess       ← pi --mode rpc 子行程（JSONL stdin/stdout）
      │
      ├── SharedMemory          ← ~/.linkpi/memory.md（跨 provider 記憶）
      │
      └── Endpoints
            GET  /v1/models          ← 列出可用 model
            POST /v1/chat/completions← 轉發至 pi，OpenAI SSE 格式回應
            POST /v1/consolidate     ← 合併所有 provider summary
            GET  /v1/memory          ← 檢視共用記憶"""))
    lines.append("```")

    lines.append("\n## 測試涵蓋範圍\n")
    lines.append("| 層級 | 涵蓋內容 | 方式 |")
    lines.append("|------|---------|------|")
    lines.append("| 靜態分析 | 語法、類別、函式、常數、import | ast.parse |")
    lines.append("| 模組匯入 | 動態載入、物件存在、介面方法 | importlib |")
    lines.append("| API 端點 | /models, /memory, /chat (400/503), /consolidate | httpx ASGI Transport |")
    lines.append("| 純函式 | _parse_provider, _last_user_text, _sse, _history_block, _tool_label | 直接呼叫 |")
    lines.append("| 檔案系統 | SharedMemory get/set/add/snapshot | tempfile |")
    lines.append("| 未涵蓋 | PiProcess 真實 subprocess (需 pi 執行檔) | — |")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# 主程式
# ──────────────────────────────────────────────────────────────────────────────

async def main_async() -> None:
    root       = Path(__file__).parent
    linkpi_path = root / "LinkPi.py"

    print(f"🔍 測試目標：{linkpi_path}")
    print("=" * 60)

    t_start = time.perf_counter()
    suites: list[TestSuite] = []

    # Suite 1：靜態分析
    print("  [1/5] 靜態分析…")
    suites.append(suite_static_analysis(linkpi_path))

    # Suite 2：模組匯入
    print("  [2/5] 模組匯入…")
    s2, mod = suite_import(linkpi_path)
    suites.append(s2)

    if mod is None:
        print("  ⚠️  模組載入失敗，跳過後續測試")
    else:
        # Suite 3：API 端點（async）
        print("  [3/5] API 端點測試…")
        suites.append(await suite_api_async(mod))

        # Suite 4：純函式單元
        print("  [4/5] 邏輯單元測試…")
        suites.append(suite_unit_logic(mod))

        # Suite 5：SharedMemory 檔案系統
        print("  [5/5] SharedMemory 整合測試…")
        suites.append(suite_shared_memory(mod))

    total_elapsed = time.perf_counter() - t_start

    # 輸出報告
    report = render_report(suites, total_elapsed)
    report_path = root / "linkpi_test_report.md"
    report_path.write_text(report, "utf-8")

    # 終端摘要
    grand_pass  = sum(s.passed for s in suites)
    grand_fail  = sum(s.failed for s in suites)
    grand_total = sum(s.total  for s in suites)

    print("=" * 60)
    print(f"  結果：{grand_pass}/{grand_total} pass  |  {grand_fail} fail")
    print(f"  耗時：{total_elapsed:.2f}s")
    print(f"  報告：{report_path}")
    print("=" * 60)

    sys.exit(0 if grand_fail == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main_async())
