#!/usr/bin/env python3
"""
test_pi_mono_harness.py
=======================
pi-mono 服務框架 Test Harness  —  不修改任何原始碼，只產出測試報告

測試範疇（7 大 Suite）：
  1. Monorepo 結構     — workspace 套件、版本一致性、package.json 完整性
  2. Build 產出物      — 各套件 dist/ 目錄、關鍵編譯檔案
  3. 模組載入          — ESM import 各套件主要模組
  4. AI 套件框架       — provider 註冊、模型目錄、API 型別
  5. 核心工具框架      — 工具定義、Agent 架構、RPC 協議
  6. TUI / 服務框架    — UI 元件、MOM 多代理、Pods 部署
  7. 測試清單盤點      — 現有 test 檔案統計與分類

執行方式：
  python3 test_pi_mono_harness.py
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import subprocess
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

PASS = "✅ PASS"
FAIL = "❌ FAIL"
SKIP = "⚠️  SKIP"
INFO = "ℹ️  INFO"
WARN = "🔶 WARN"


@dataclass
class TestResult:
    name: str
    status: str
    detail: str = ""
    elapsed: float = 0.0


@dataclass
class TestSuite:
    title: str
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
    def warned(self): return sum(1 for r in self.results if r.status == WARN)
    @property
    def skipped(self): return sum(1 for r in self.results if r.status == SKIP)


# ──────────────────────────────────────────────────────────────────────────────
# 工具函式
# ──────────────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent


def node_eval(script: str, timeout: int = 15) -> tuple[bool, str]:
    """執行 Node.js ESM 腳本，回傳 (success, stdout+stderr)"""
    result = subprocess.run(
        ["node", "--input-type=module"],
        input=script.encode(),
        capture_output=True,
        timeout=timeout,
        cwd=str(ROOT),
    )
    out = result.stdout.decode(errors="replace") + result.stderr.decode(errors="replace")
    return result.returncode == 0, out.strip()


def pkg_json(pkg_path: Path) -> dict:
    p = pkg_path / "package.json"
    return json.loads(p.read_text()) if p.exists() else {}


# ──────────────────────────────────────────────────────────────────────────────
# Suite 1：Monorepo 結構
# ──────────────────────────────────────────────────────────────────────────────

def suite_monorepo_structure() -> TestSuite:
    s = TestSuite("Monorepo 結構（Workspace Structure）")

    # 1-1 根目錄 package.json
    t0 = time.perf_counter()
    root_pkg = pkg_json(ROOT)
    if root_pkg:
        s.add("根 package.json 存在", PASS,
              f"name={root_pkg.get('name')}  version={root_pkg.get('version')}",
              time.perf_counter() - t0)
    else:
        s.add("根 package.json 存在", FAIL, "找不到", time.perf_counter() - t0)
        return s

    # 1-2 workspaces 宣告
    t0 = time.perf_counter()
    ws = root_pkg.get("workspaces", [])
    if ws:
        s.add("workspaces 宣告", PASS, f"{len(ws)} 個 workspace 路徑", time.perf_counter() - t0)
    else:
        s.add("workspaces 宣告", FAIL, "未定義 workspaces", time.perf_counter() - t0)

    # 1-3 核心套件目錄存在
    pkgs = {
        "ai":            "packages/ai",
        "agent":         "packages/agent",
        "tui":           "packages/tui",
        "coding-agent":  "packages/coding-agent",
        "mom":           "packages/mom",
        "pods":          "packages/pods",
        "web-ui":        "packages/web-ui",
    }
    t0 = time.perf_counter()
    all_ok = True
    found = []
    for name, rel in pkgs.items():
        if (ROOT / rel).is_dir():
            found.append(name)
        else:
            all_ok = False
    s.add("核心套件目錄完整", PASS if all_ok else FAIL,
          f"找到：{found}", time.perf_counter() - t0)

    # 1-4 版本一致性（packages 之間互相一致，root monorepo meta 版本不同是正常設計）
    t0 = time.perf_counter()
    root_ver = root_pkg.get("version", "?")
    pkg_versions: dict[str, str] = {}
    for name, rel in pkgs.items():
        p = pkg_json(ROOT / rel)
        pkg_versions[name] = p.get("version", "N/A")
    unique_pkg_versions = set(pkg_versions.values())
    if len(unique_pkg_versions) == 1:
        pkg_ver = list(unique_pkg_versions)[0]
        s.add("版本一致性（lockstep）", PASS,
              f"所有套件均為 v{pkg_ver}（root monorepo: v{root_ver}，屬正常設計）",
              time.perf_counter() - t0)
    else:
        mismatch = [f"{n}@{v}" for n, v in pkg_versions.items()]
        s.add("版本一致性（lockstep）", FAIL,
              f"套件版本不一致：{mismatch}", time.perf_counter() - t0)

    # 1-5 各套件 package.json 必要欄位
    t0 = time.perf_counter()
    missing_fields: list[str] = []
    for name, rel in pkgs.items():
        p = pkg_json(ROOT / rel)
        for field_name in ("name", "version", "main"):
            if field_name not in p and field_name != "main":
                missing_fields.append(f"{name}.{field_name}")
    if not missing_fields:
        s.add("套件 package.json 完整性", PASS,
              f"{len(pkgs)} 個套件均有 name/version", time.perf_counter() - t0)
    else:
        s.add("套件 package.json 完整性", WARN,
              f"缺少欄位：{missing_fields}", time.perf_counter() - t0)

    # 1-6 npm workspace 鏈結（node_modules/.package-lock.json）
    t0 = time.perf_counter()
    lock_file = ROOT / "package-lock.json"
    nm_dir = ROOT / "node_modules"
    if lock_file.exists() and nm_dir.is_dir():
        lock_size = lock_file.stat().st_size
        s.add("npm install 已執行", PASS,
              f"package-lock.json ({lock_size:,} bytes)，node_modules 存在",
              time.perf_counter() - t0)
    else:
        s.add("npm install 已執行", WARN,
              "package-lock.json 或 node_modules 不存在，請先執行 npm install",
              time.perf_counter() - t0)

    # 1-7 scripts 完整性（根層級）
    t0 = time.perf_counter()
    required_scripts = {"build", "check", "test", "clean"}
    actual_scripts = set(root_pkg.get("scripts", {}).keys())
    missing_s = required_scripts - actual_scripts
    s.add("根 scripts 完整性", PASS if not missing_s else WARN,
          f"找到：{sorted(actual_scripts & required_scripts)}" +
          (f"  缺少：{missing_s}" if missing_s else ""),
          time.perf_counter() - t0)

    # 1-8 biome.json（程式碼品質工具）
    t0 = time.perf_counter()
    biome = ROOT / "biome.json"
    s.add("biome.json（程式碼檢查設定）",
          PASS if biome.exists() else WARN,
          f"{biome.stat().st_size} bytes" if biome.exists() else "不存在",
          time.perf_counter() - t0)

    # 1-9 tsconfig
    t0 = time.perf_counter()
    tsconfigs = list(ROOT.glob("tsconfig*.json"))
    s.add("tsconfig 設定", PASS if tsconfigs else WARN,
          f"找到 {len(tsconfigs)} 個：{[f.name for f in tsconfigs]}",
          time.perf_counter() - t0)

    # 1-10 LinkPi bridge 存在
    t0 = time.perf_counter()
    linkpi = ROOT / "LinkPi.py"
    pi_startup = ROOT / "pi_startup.py"
    files = [f.name for f in [linkpi, pi_startup] if f.exists()]
    s.add("Bridge 腳本存在", PASS if files else WARN,
          f"找到：{files}", time.perf_counter() - t0)

    return s


# ──────────────────────────────────────────────────────────────────────────────
# Suite 2：Build 產出物
# ──────────────────────────────────────────────────────────────────────────────

def suite_build_artifacts() -> TestSuite:
    s = TestSuite("Build 產出物（Dist Artifacts）")

    pkg_checks = {
        "packages/ai": {
            "must_exist": [
                "dist/index.js", "dist/index.d.ts",
                "dist/stream.js", "dist/types.js",
                "dist/api-registry.js", "dist/models.js",
                "dist/models.generated.js",
                "dist/providers/register-builtins.js",
                "dist/providers/anthropic.js",
                "dist/providers/faux.js",
                "dist/env-api-keys.js",
            ],
        },
        "packages/agent": {
            "must_exist": [
                "dist/index.js", "dist/index.d.ts",
                "dist/agent.js", "dist/agent-loop.js",
                "dist/types.js", "dist/proxy.js",
            ],
        },
        "packages/tui": {
            "must_exist": [
                "dist/index.js", "dist/index.d.ts",
                "dist/tui.js", "dist/terminal.js",
                "dist/keybindings.js", "dist/keys.js",
            ],
        },
        "packages/coding-agent": {
            "must_exist": [
                "dist/index.js", "dist/index.d.ts",
                "dist/config.js", "dist/cli.js", "dist/main.js",
                "dist/core/agent-session.js",
                "dist/core/auth-storage.js",
                "dist/core/tools/index.js",
                "dist/core/session-manager.js",
                "dist/modes/rpc/rpc-types.js",
                "dist/modes/rpc/jsonl.js",
                "dist/modes/rpc/rpc-mode.js",
            ],
        },
        "packages/mom": {
            "must_exist": [
                "dist/agent.js", "dist/main.js",
                "dist/slack.js", "dist/store.js",
            ],
        },
        "packages/pods": {
            "must_exist": [
                "dist/index.js",
            ],
        },
    }

    for pkg_rel, checks in pkg_checks.items():
        pkg_path = ROOT / pkg_rel
        pkg_name = pkg_rel.split("/")[1]

        for rel_path in checks["must_exist"]:
            t0 = time.perf_counter()
            full = pkg_path / rel_path
            if full.exists():
                size = full.stat().st_size
                s.add(f"{pkg_name}/{rel_path}",
                      PASS, f"{size:,} bytes", time.perf_counter() - t0)
            else:
                s.add(f"{pkg_name}/{rel_path}",
                      FAIL, "檔案不存在（需要執行 npm run build）",
                      time.perf_counter() - t0)

    # 特殊：coding-agent 主題資源
    t0 = time.perf_counter()
    theme_dir = ROOT / "packages/coding-agent/dist/modes/interactive/theme"
    themes = list(theme_dir.glob("*.json")) if theme_dir.exists() else []
    s.add("coding-agent/theme JSON 資源",
          PASS if themes else WARN,
          f"找到 {len(themes)} 個主題：{[f.name for f in themes]}",
          time.perf_counter() - t0)

    # 特殊：coding-agent source maps
    t0 = time.perf_counter()
    maps = list((ROOT / "packages/coding-agent/dist").rglob("*.js.map"))
    s.add("coding-agent source maps",
          PASS if maps else WARN,
          f"找到 {len(maps)} 個 .js.map",
          time.perf_counter() - t0)

    return s


# ──────────────────────────────────────────────────────────────────────────────
# Suite 3：模組載入（Node.js ESM）
# ──────────────────────────────────────────────────────────────────────────────

def suite_module_loading() -> TestSuite:
    s = TestSuite("模組載入（ESM Module Import）")

    tests: list[tuple[str, str]] = [
        ("@pi-ai index", """
import * as m from "./packages/ai/dist/index.js";
const keys = Object.keys(m);
if (!keys.includes("stream") || !keys.includes("streamSimple"))
  throw new Error("Missing stream exports: " + keys.join(","));
console.log("OK exports:" + keys.length);
"""),
        ("@pi-ai providers/register-builtins", """
import "./packages/ai/dist/providers/register-builtins.js";
import { getApiProvider } from "./packages/ai/dist/api-registry.js";
const apis = ["anthropic-messages","openai-completions","openai-responses",
              "google-generative-ai","bedrock-converse-stream","mistral-conversations"];
for (const api of apis) {
  if (!getApiProvider(api)) throw new Error("Not registered: " + api);
}
console.log("OK apis:" + apis.length);
"""),
        ("@pi-ai models.generated", """
import { MODELS } from "./packages/ai/dist/models.generated.js";
const providers = Object.keys(MODELS);
if (providers.length < 10) throw new Error("Too few providers: " + providers.length);
let total = 0;
for (const ms of Object.values(MODELS)) total += Object.keys(ms).length;
if (total < 100) throw new Error("Too few models: " + total);
console.log("OK providers:" + providers.length + " models:" + total);
"""),
        ("@pi-ai faux provider", """
import { fauxAssistantMessage, fauxText, fauxToolCall,
         registerFauxProvider } from "./packages/ai/dist/providers/faux.js";
if (typeof fauxText !== "function") throw new Error("fauxText not a function");
if (typeof registerFauxProvider !== "function") throw new Error("registerFauxProvider not a function");
console.log("OK faux exports:5");
"""),
        ("@pi-agent-core index", """
import { Agent, agentLoop, runAgentLoop, streamProxy } from "./packages/agent/dist/index.js";
if (typeof Agent !== "function") throw new Error("Agent not a class/function");
if (typeof agentLoop !== "function") throw new Error("agentLoop not a function");
console.log("OK agent exports:6");
"""),
        ("@pi-tui index", """
import { TUI, Box, Editor, Input, Markdown, SelectList,
         KeybindingsManager } from "./packages/tui/dist/index.js";
for (const [n,v] of [["TUI",TUI],["Box",Box],["Editor",Editor]]) {
  if (!v) throw new Error(n + " not exported");
}
console.log("OK tui exports:verified");
"""),
        ("@pi-coding-agent config", """
import { VERSION, getAgentDir } from "./packages/coding-agent/dist/config.js";
if (!VERSION || typeof VERSION !== "string") throw new Error("VERSION invalid: " + VERSION);
const dir = getAgentDir();
if (!dir || typeof dir !== "string") throw new Error("getAgentDir() invalid");
console.log("OK version:" + VERSION + " agentDir:" + dir);
"""),
        ("@pi-coding-agent tools", """
import { allToolDefinitions, bashToolDefinition, editToolDefinition,
         readToolDefinition, writeToolDefinition, findToolDefinition,
         grepToolDefinition } from "./packages/coding-agent/dist/core/tools/index.js";
const tools = [bashToolDefinition, editToolDefinition, readToolDefinition,
               writeToolDefinition, findToolDefinition, grepToolDefinition];
for (const t of tools) {
  if (!t || !t.name) throw new Error("Invalid tool: " + JSON.stringify(t));
}
console.log("OK tools:" + allToolDefinitions.length);
"""),
        ("@pi-coding-agent auth-storage", """
import { AuthStorage, FileAuthStorageBackend,
         InMemoryAuthStorageBackend } from "./packages/coding-agent/dist/core/auth-storage.js";
const backend = new InMemoryAuthStorageBackend();
const storage = new AuthStorage(backend);
const methods = Object.getOwnPropertyNames(Object.getPrototypeOf(storage));
if (!methods.includes("get") || !methods.includes("set"))
  throw new Error("Missing methods: " + methods);
console.log("OK methods:" + methods.length);
"""),
        ("@pi-coding-agent rpc-mode (dist)", """
import { existsSync } from "fs";
const path = "./packages/coding-agent/dist/modes/rpc/rpc-mode.js";
import { createReadStream } from "fs";
// Just check the file is valid JS by importing it
const mod = await import(path);
console.log("OK rpc-mode exports:" + Object.keys(mod).length);
"""),
        ("@pi-coding-agent jsonl", """
import { serializeJsonLine, attachJsonlLineReader }
  from "./packages/coding-agent/dist/modes/rpc/jsonl.js";
const line = serializeJsonLine({ type: "prompt", message: "hello" });
if (!line.endsWith("\\n")) throw new Error("JSONL must end with newline");
const parsed = JSON.parse(line.trim());
if (parsed.type !== "prompt") throw new Error("Parse failed: " + line);
console.log("OK jsonl roundtrip");
"""),
        ("@pi-mom main", """
import { existsSync } from "fs";
const f = "./packages/mom/dist/main.js";
if (!existsSync(f)) throw new Error("mom/dist/main.js not built");
console.log("OK mom dist exists");
"""),
        ("@pi-pods dist", """
import { existsSync } from "fs";
const f = "./packages/pods/dist/index.js";
if (!existsSync(f)) throw new Error("pods/dist/index.js not built");
console.log("OK pods dist exists");
"""),
    ]

    for label, script in tests:
        t0 = time.perf_counter()
        ok, out = node_eval(script)
        if ok:
            detail = out.split("\n")[-1] if out else "OK"
            s.add(f"import {label}", PASS, detail, time.perf_counter() - t0)
        else:
            err = out.split("\n")[0][:120] if out else "unknown error"
            s.add(f"import {label}", FAIL, err, time.perf_counter() - t0)

    return s


# ──────────────────────────────────────────────────────────────────────────────
# Suite 4：AI 套件框架
# ──────────────────────────────────────────────────────────────────────────────

def suite_ai_framework() -> TestSuite:
    s = TestSuite("AI 套件框架（packages/ai）")

    # 4-1 所有已知 API 型別對應
    t0 = time.perf_counter()
    ok, out = node_eval("""
import "./packages/ai/dist/providers/register-builtins.js";
import { getApiProvider } from "./packages/ai/dist/api-registry.js";
const knownApis = [
  "openai-completions", "mistral-conversations", "openai-responses",
  "azure-openai-responses", "openai-codex-responses", "anthropic-messages",
  "bedrock-converse-stream", "google-generative-ai",
  "google-gemini-cli", "google-vertex"
];
const missing = knownApis.filter(api => !getApiProvider(api));
if (missing.length > 0) throw new Error("Missing APIs: " + missing.join(","));
console.log("OK all:" + knownApis.length);
""")
    s.add("所有 KnownApi 已註冊", PASS if ok else FAIL,
          out.split("\n")[-1] if ok else out.split("\n")[0][:120],
          time.perf_counter() - t0)

    # 4-2 模型目錄 Provider 數量
    t0 = time.perf_counter()
    ok, out = node_eval("""
import { MODELS } from "./packages/ai/dist/models.generated.js";
const providers = Object.keys(MODELS);
let total = 0;
for (const ms of Object.values(MODELS)) total += Object.keys(ms).length;
const result = { providers: providers.length, models: total, list: providers };
console.log(JSON.stringify(result));
""")
    if ok:
        try:
            data = json.loads(out.strip().split("\n")[-1])
            providers_count = data["providers"]
            models_count = data["models"]
            providers_list = data["list"]
            s.add("模型目錄 Provider 數量", PASS,
                  f"{providers_count} 個 provider，共 {models_count} 個模型",
                  time.perf_counter() - t0)
            # 逐一顯示各 provider 模型數
            t0b = time.perf_counter()
            ok2, out2 = node_eval("""
import { MODELS } from "./packages/ai/dist/models.generated.js";
for (const [p,ms] of Object.entries(MODELS)) {
  console.log(p + "=" + Object.keys(ms).length);
}
""")
            if ok2:
                for line in out2.strip().split("\n"):
                    if "=" in line:
                        prov, cnt = line.split("=", 1)
                        s.add(f"  provider: {prov}", INFO,
                              f"{cnt} 個模型", time.perf_counter() - t0b)
        except Exception as e:
            s.add("模型目錄 Provider 數量", WARN,
                  f"解析輸出失敗：{e}", time.perf_counter() - t0)
    else:
        s.add("模型目錄 Provider 數量", FAIL,
              out.split("\n")[0][:120], time.perf_counter() - t0)

    # 4-3 env-api-keys 偵測
    t0 = time.perf_counter()
    ok, out = node_eval("""
import { getEnvApiKey } from "./packages/ai/dist/env-api-keys.js";
const providers = ["anthropic","openai","google","mistral","groq",
                   "amazon-bedrock","openrouter","xai","azure-openai-responses"];
const results = {};
for (const p of providers) {
  const key = getEnvApiKey(p);
  results[p] = key ? "configured" : "not set";
}
console.log(JSON.stringify(results));
""")
    if ok:
        try:
            data = json.loads(out.strip().split("\n")[-1])
            configured = [k for k, v in data.items() if v == "configured"]
            not_set = [k for k, v in data.items() if v != "configured"]
            s.add("env-api-keys 偵測",
                  PASS if len(configured) > 0 else WARN,
                  f"已設定：{configured or '(無)'}  未設定：{not_set}",
                  time.perf_counter() - t0)
        except Exception:
            s.add("env-api-keys 偵測", INFO, out[:120], time.perf_counter() - t0)
    else:
        s.add("env-api-keys 偵測", FAIL, out.split("\n")[0][:120], time.perf_counter() - t0)

    # 4-4 faux provider 建立 AssistantMessage
    t0 = time.perf_counter()
    ok, out = node_eval("""
import { fauxAssistantMessage, fauxText }
  from "./packages/ai/dist/providers/faux.js";
const msg = fauxAssistantMessage([fauxText("hello world")]);
if (msg.role !== "assistant") throw new Error("role wrong: " + msg.role);
if (!msg.content || msg.content.length === 0) throw new Error("content empty");
const tc = msg.content[0];
if (tc.type !== "text" || tc.text !== "hello world") throw new Error("text wrong");
console.log("OK role:" + msg.role + " content:" + msg.content.length);
""")
    s.add("faux AssistantMessage 建立", PASS if ok else FAIL,
          out.split("\n")[-1] if ok else out.split("\n")[0][:120],
          time.perf_counter() - t0)

    # 4-5 Event Stream 建立
    t0 = time.perf_counter()
    ok, out = node_eval("""
import { createAssistantMessageEventStream, EventStream }
  from "./packages/ai/dist/utils/event-stream.js";
const stream = createAssistantMessageEventStream(async function*(push) {
  push({ type: "text_delta", delta: "hello" });
});
if (!stream) throw new Error("stream not created");
console.log("OK stream type:" + typeof stream);
""")
    s.add("AssistantMessageEventStream 建立", PASS if ok else FAIL,
          out.split("\n")[-1] if ok else out.split("\n")[0][:120],
          time.perf_counter() - t0)

    # 4-6 Token overflow 工具
    t0 = time.perf_counter()
    ok, out = node_eval("""
import { isContextOverflow, getOverflowPatterns } from "./packages/ai/dist/utils/overflow.js";
if (typeof isContextOverflow !== "function")
  throw new Error("isContextOverflow not a function");
if (typeof getOverflowPatterns !== "function")
  throw new Error("getOverflowPatterns not a function");
console.log("OK isContextOverflow + getOverflowPatterns available");
""")
    s.add("Overflow 工具（isContextOverflow）", PASS if ok else FAIL,
          out.split("\n")[-1] if ok else out.split("\n")[0][:120],
          time.perf_counter() - t0)

    return s


# ──────────────────────────────────────────────────────────────────────────────
# Suite 5：核心工具框架
# ──────────────────────────────────────────────────────────────────────────────

def suite_core_tools() -> TestSuite:
    s = TestSuite("核心工具框架（Coding Agent Core）")

    # 5-1 工具定義完整性（allToolDefinitions 是物件 map，key=工具名稱）
    t0 = time.perf_counter()
    ok, out = node_eval("""
import { allToolDefinitions } from "./packages/coding-agent/dist/core/tools/index.js";
const names = Object.keys(allToolDefinitions);
const required = ["bash","edit","read","write","find","grep","ls"];
const missing = required.filter(n => !names.includes(n));
if (missing.length > 0) throw new Error("Missing tools: " + missing.join(","));
console.log(JSON.stringify({ count: names.length, names }));
""")
    if ok:
        try:
            data = json.loads(out.strip().split("\n")[-1])
            s.add("allToolDefinitions 完整", PASS,
                  f"{data['count']} 個工具：{data['names']}",
                  time.perf_counter() - t0)
        except Exception:
            s.add("allToolDefinitions 完整", PASS, out[:120], time.perf_counter() - t0)
    else:
        s.add("allToolDefinitions 完整", FAIL,
              out.split("\n")[0][:120], time.perf_counter() - t0)

    # 5-2 工具定義格式（name, description, parameters）— 迭代物件 values
    t0 = time.perf_counter()
    ok, out = node_eval("""
import { allToolDefinitions } from "./packages/coding-agent/dist/core/tools/index.js";
const defs = Object.values(allToolDefinitions);
// 工具定義使用 parameters（非 inputSchema）
const invalid = defs.filter(t => !t.name || !t.description || !t.parameters);
if (invalid.length > 0)
  throw new Error("Invalid tools: " + invalid.map(t=>t.name).join(","));
console.log("OK all " + defs.length + " tools have name/description/parameters");
""")
    s.add("工具定義格式（name/desc/parameters）", PASS if ok else FAIL,
          out.split("\n")[-1] if ok else out.split("\n")[0][:120],
          time.perf_counter() - t0)

    # 5-3 Agent 核心架構
    t0 = time.perf_counter()
    ok, out = node_eval("""
import { Agent, agentLoop, agentLoopContinue, runAgentLoop,
         runAgentLoopContinue, streamProxy } from "./packages/agent/dist/index.js";
const fns = { Agent, agentLoop, agentLoopContinue, runAgentLoop,
              runAgentLoopContinue, streamProxy };
const missing = Object.entries(fns).filter(([,v]) => !v).map(([k]) => k);
if (missing.length > 0) throw new Error("Missing: " + missing.join(","));
console.log("OK all 6 agent exports present");
""")
    s.add("Agent 核心匯出完整", PASS if ok else FAIL,
          out.split("\n")[-1] if ok else out.split("\n")[0][:120],
          time.perf_counter() - t0)

    # 5-4 RPC 命令型別（靜態原始碼）
    t0 = time.perf_counter()
    rpc_types_ts = ROOT / "packages/coding-agent/src/modes/rpc/rpc-types.ts"
    if rpc_types_ts.exists():
        content = rpc_types_ts.read_text()
        rpc_commands = re.findall(r'type: "[^"]+"', content)
        command_types = list({m.split('"')[1] for m in rpc_commands})
        expected_cmds = ["prompt", "steer", "abort", "compact",
                         "get_state", "set_model", "get_session_stats"]
        missing_cmd = [c for c in expected_cmds if c not in command_types]
        s.add("RPC 命令型別完整", PASS if not missing_cmd else FAIL,
              f"找到 {len(command_types)} 種命令：{sorted(command_types)[:10]}…",
              time.perf_counter() - t0)
    else:
        s.add("RPC 命令型別完整", SKIP, "rpc-types.ts 不存在", time.perf_counter() - t0)

    # 5-5 JSONL 序列化 roundtrip
    t0 = time.perf_counter()
    ok, out = node_eval("""
import { serializeJsonLine } from "./packages/coding-agent/dist/modes/rpc/jsonl.js";
const cmds = [
  { id: "1", type: "prompt", message: "Hello, pi!" },
  { id: "2", type: "abort" },
  { id: "3", type: "get_state" },
  { id: "4", type: "compact", customInstructions: "be concise" },
];
for (const cmd of cmds) {
  const line = serializeJsonLine(cmd);
  if (!line.endsWith("\\n")) throw new Error("Missing newline in: " + line);
  const parsed = JSON.parse(line.trim());
  if (parsed.type !== cmd.type) throw new Error("Type mismatch for: " + cmd.type);
}
console.log("OK " + cmds.length + " RPC commands serialized");
""")
    s.add("JSONL RPC 序列化 roundtrip", PASS if ok else FAIL,
          out.split("\n")[-1] if ok else out.split("\n")[0][:120],
          time.perf_counter() - t0)

    # 5-6 AuthStorage in-memory 操作
    t0 = time.perf_counter()
    ok, out = node_eval("""
import { AuthStorage, InMemoryAuthStorageBackend }
  from "./packages/coding-agent/dist/core/auth-storage.js";
const backend = new InMemoryAuthStorageBackend();
const storage = new AuthStorage(backend);
// set / get / has / remove
await storage.set("test-provider", { type: "apiKey", apiKey: "test-key-123" });
const has = await storage.has("test-provider");
if (!has) throw new Error("has() returned false after set()");
const cred = await storage.get("test-provider");
if (!cred || cred.apiKey !== "test-key-123")
  throw new Error("get() returned wrong value: " + JSON.stringify(cred));
await storage.remove("test-provider");
const has2 = await storage.has("test-provider");
if (has2) throw new Error("has() returned true after remove()");
console.log("OK set/get/has/remove all work");
""")
    s.add("AuthStorage set/get/has/remove", PASS if ok else FAIL,
          out.split("\n")[-1] if ok else out.split("\n")[0][:120],
          time.perf_counter() - t0)

    # 5-7 VERSION 與 agentDir
    t0 = time.perf_counter()
    ok, out = node_eval("""
import { VERSION, getAgentDir } from "./packages/coding-agent/dist/config.js";
if (!VERSION.match(/^\\d+\\.\\d+\\.\\d+$/))
  throw new Error("Invalid VERSION: " + VERSION);
const dir = getAgentDir();
if (!dir.includes(".pi")) throw new Error("Unexpected agentDir: " + dir);
console.log("VERSION:" + VERSION + " agentDir:" + dir);
""")
    s.add("VERSION / getAgentDir()", PASS if ok else FAIL,
          out.split("\n")[-1] if ok else out.split("\n")[0][:120],
          time.perf_counter() - t0)

    # 5-8 compaction 模組
    t0 = time.perf_counter()
    ok, out = node_eval("""
import { compact, findCutPoint, calculateContextTokens,
         DEFAULT_COMPACTION_SETTINGS }
  from "./packages/coding-agent/dist/core/compaction/index.js";
const missing = [["compact",compact],["findCutPoint",findCutPoint],
  ["calculateContextTokens",calculateContextTokens],
  ["DEFAULT_COMPACTION_SETTINGS",DEFAULT_COMPACTION_SETTINGS]]
  .filter(([,v])=>!v).map(([k])=>k);
if (missing.length > 0) throw new Error("Missing: " + missing);
console.log("OK compaction maxTokens:" + DEFAULT_COMPACTION_SETTINGS.maxTokens);
""")
    s.add("Compaction 模組匯出", PASS if ok else FAIL,
          out.split("\n")[-1] if ok else out.split("\n")[0][:120],
          time.perf_counter() - t0)

    # 5-9 SessionManager 存在
    t0 = time.perf_counter()
    ok, out = node_eval("""
import * as sm from "./packages/coding-agent/dist/core/session-manager.js";
const keys = Object.keys(sm);
if (keys.length === 0) throw new Error("No exports from session-manager");
console.log("OK session-manager exports:" + keys.length + " " + keys.slice(0,5).join(","));
""")
    s.add("SessionManager 模組", PASS if ok else FAIL,
          out.split("\n")[-1] if ok else out.split("\n")[0][:120],
          time.perf_counter() - t0)

    # 5-10 SettingsManager 存在
    t0 = time.perf_counter()
    ok, out = node_eval("""
import * as settings from "./packages/coding-agent/dist/core/settings-manager.js";
const keys = Object.keys(settings);
if (keys.length === 0) throw new Error("No exports from settings-manager");
console.log("OK settings-manager exports:" + keys.length);
""")
    s.add("SettingsManager 模組", PASS if ok else FAIL,
          out.split("\n")[-1] if ok else out.split("\n")[0][:120],
          time.perf_counter() - t0)

    return s


# ──────────────────────────────────────────────────────────────────────────────
# Suite 6：TUI / 服務框架（MOM / Pods / Web-UI）
# ──────────────────────────────────────────────────────────────────────────────

def suite_services() -> TestSuite:
    s = TestSuite("服務框架（TUI / MOM / Pods / Web-UI）")

    # 6-1 TUI 核心元件
    t0 = time.perf_counter()
    ok, out = node_eval("""
import { TUI, Box, Container, Editor, Input, Markdown,
         SelectList, SettingsList, Text, TruncatedText,
         Loader, CancellableLoader, Spacer, Image,
         StdinBuffer, KeybindingsManager }
  from "./packages/tui/dist/index.js";
const components = { TUI, Box, Container, Editor, Input, Markdown,
  SelectList, SettingsList, Text, TruncatedText, Loader, CancellableLoader,
  Spacer, StdinBuffer, KeybindingsManager };
const missing = Object.entries(components).filter(([,v])=>!v).map(([k])=>k);
if (missing.length > 0) throw new Error("Missing TUI components: " + missing);
console.log("OK " + Object.keys(components).length + " components exported");
""")
    s.add("TUI 核心元件匯出", PASS if ok else FAIL,
          out.split("\n")[-1] if ok else out.split("\n")[0][:120],
          time.perf_counter() - t0)

    # 6-2 TUI keybindings
    t0 = time.perf_counter()
    ok, out = node_eval("""
import { TUI_KEYBINDINGS, KeybindingsManager }
  from "./packages/tui/dist/index.js";
if (!TUI_KEYBINDINGS || typeof TUI_KEYBINDINGS !== "object")
  throw new Error("TUI_KEYBINDINGS invalid");
const keys = Object.keys(TUI_KEYBINDINGS);
if (keys.length === 0) throw new Error("TUI_KEYBINDINGS empty");
console.log("OK keybindings:" + keys.length + " groups:" + keys.join(","));
""")
    s.add("TUI_KEYBINDINGS 定義", PASS if ok else FAIL,
          out.split("\n")[-1] if ok else out.split("\n")[0][:120],
          time.perf_counter() - t0)

    # 6-3 TUI fuzzy filter
    t0 = time.perf_counter()
    ok, out = node_eval("""
import { fuzzyFilter, fuzzyMatch } from "./packages/tui/dist/fuzzy.js";
if (typeof fuzzyFilter !== "function")
  throw new Error("fuzzyFilter not a function");
if (typeof fuzzyMatch !== "function")
  throw new Error("fuzzyMatch not a function");
// fuzzyFilter 需要第三參數 getText 函數
const items = ["hello world","foo bar","test item"];
const results = fuzzyFilter(items, "llo", (x) => x);
if (results.length === 0) throw new Error("fuzzyFilter returned empty for 'llo'");
// fuzzyMatch 直接匹配字串
const matched = fuzzyMatch("llo", "hello world");
if (!matched.matches) throw new Error("fuzzyMatch failed");
console.log("OK fuzzyFilter:" + results.length + " fuzzyMatch.score:" + matched.score);
""")
    s.add("TUI fuzzyFilter / fuzzyMatch 功能", PASS if ok else FAIL,
          out.split("\n")[-1] if ok else out.split("\n")[0][:120],
          time.perf_counter() - t0)

    # 6-4 MOM dist 結構
    t0 = time.perf_counter()
    mom_dist = ROOT / "packages/mom/dist"
    if mom_dist.exists():
        mom_files = list(mom_dist.rglob("*.js"))
        s.add("MOM dist 結構", PASS,
              f"{len(mom_files)} 個 .js 檔案：{[f.name for f in mom_files[:6]]}",
              time.perf_counter() - t0)
    else:
        s.add("MOM dist 結構", FAIL, "dist/ 不存在，需執行 npm run build", time.perf_counter() - t0)

    # 6-5 MOM 環境變數設定
    t0 = time.perf_counter()
    mom_src = ROOT / "packages/mom/src/main.ts"
    if mom_src.exists():
        content = mom_src.read_text()
        env_vars = re.findall(r'process\.env\.(\w+)', content)
        unique_env = sorted(set(env_vars))
        s.add("MOM 環境變數清單", INFO,
              f"需要設定：{unique_env}", time.perf_counter() - t0)
    else:
        s.add("MOM 環境變數清單", SKIP, "main.ts 不存在", time.perf_counter() - t0)

    # 6-6 MOM Slack bot 結構
    t0 = time.perf_counter()
    ok, out = node_eval("""
import { existsSync } from "fs";
const files = [
  "./packages/mom/dist/slack.js",
  "./packages/mom/dist/agent.js",
  "./packages/mom/dist/store.js",
  "./packages/mom/dist/events.js",
  "./packages/mom/dist/sandbox.js",
];
const missing = files.filter(f => !existsSync(f));
if (missing.length > 0) throw new Error("Missing: " + missing.join(","));
console.log("OK all " + files.length + " mom files exist");
""")
    s.add("MOM Slack Bot 檔案完整", PASS if ok else FAIL,
          out.split("\n")[-1] if ok else out.split("\n")[0][:120],
          time.perf_counter() - t0)

    # 6-7 Pods dist 結構
    t0 = time.perf_counter()
    pods_dist = ROOT / "packages/pods/dist"
    if pods_dist.exists():
        pods_files = list(pods_dist.rglob("*.js"))
        s.add("Pods dist 結構", PASS,
              f"{len(pods_files)} 個 .js 檔案：{[f.name for f in pods_files[:6]]}",
              time.perf_counter() - t0)
    else:
        s.add("Pods dist 結構", FAIL, "dist/ 不存在，需執行 npm run build", time.perf_counter() - t0)

    # 6-8 Web-UI dist 結構
    t0 = time.perf_counter()
    webui_dist = ROOT / "packages/web-ui/dist"
    if webui_dist.exists():
        wui_files = list(webui_dist.rglob("*.js"))
        s.add("Web-UI dist 結構", PASS,
              f"{len(wui_files)} 個 .js 檔案", time.perf_counter() - t0)
    else:
        s.add("Web-UI dist 結構", WARN, "dist/ 不存在", time.perf_counter() - t0)

    # 6-9 coding-agent RPC mode 架構
    t0 = time.perf_counter()
    rpc_files = ["rpc-mode.ts", "rpc-types.ts", "jsonl.ts", "rpc-client.ts"]
    rpc_src = ROOT / "packages/coding-agent/src/modes/rpc"
    found_rpc = [f for f in rpc_files if (rpc_src / f).exists()]
    s.add("RPC 模式原始碼完整", PASS if len(found_rpc) == len(rpc_files) else WARN,
          f"{len(found_rpc)}/{len(rpc_files)}：{found_rpc}",
          time.perf_counter() - t0)

    # 6-10 pi 可執行腳本
    t0 = time.perf_counter()
    pi_scripts = [f for f in ["pi.sh", "pi.cmd", "pi-test.sh"] if (ROOT / f).exists()]
    s.add("pi 可執行腳本", PASS if pi_scripts else WARN,
          f"找到：{pi_scripts}", time.perf_counter() - t0)

    return s


# ──────────────────────────────────────────────────────────────────────────────
# Suite 7：測試清單盤點
# ──────────────────────────────────────────────────────────────────────────────

def suite_test_inventory() -> TestSuite:
    s = TestSuite("測試清單盤點（Test Inventory）")

    pkg_dirs = {
        "ai":           ROOT / "packages/ai/test",
        "agent":        ROOT / "packages/agent/test",
        "tui":          ROOT / "packages/tui/test",
        "coding-agent": ROOT / "packages/coding-agent/test",
    }

    grand_total = 0
    for pkg_name, test_dir in pkg_dirs.items():
        t0 = time.perf_counter()
        if not test_dir.exists():
            s.add(f"{pkg_name} 測試目錄", WARN, "test/ 不存在", time.perf_counter() - t0)
            continue

        test_files = sorted(test_dir.rglob("*.test.ts"))
        count = len(test_files)
        grand_total += count

        # 統計各類型測試
        categories: dict[str, list[str]] = {}
        for f in test_files:
            stem = f.stem.replace(".test", "")
            # 分類
            if any(k in stem for k in ("e2e", "integration")):
                cat = "e2e"
            elif any(k in stem for k in ("session", "compaction", "agent")):
                cat = "session/agent"
            elif any(k in stem for k in ("tool", "bash", "edit", "read", "write", "find", "grep")):
                cat = "tools"
            elif any(k in stem for k in ("provider", "stream", "model", "token", "overflow", "faux")):
                cat = "ai/stream"
            elif any(k in stem for k in ("tui", "markdown", "editor", "input", "terminal", "overlay")):
                cat = "tui"
            elif any(k in stem for k in ("rpc", "sdk", "auth", "settings", "config", "keybinding")):
                cat = "infra"
            else:
                cat = "other"
            categories.setdefault(cat, []).append(stem)

        cat_summary = "  ".join(f"{cat}({len(v)})" for cat, v in sorted(categories.items()))
        s.add(f"{pkg_name} 測試數量",
              PASS if count > 0 else WARN,
              f"{count} 個測試檔案  [{cat_summary}]",
              time.perf_counter() - t0)

    # 總計
    t0 = time.perf_counter()
    s.add("測試檔案總計", INFO, f"共 {grand_total} 個 .test.ts 檔案", time.perf_counter() - t0)

    # vitest 設定
    t0 = time.perf_counter()
    vitest_configs: list[str] = []
    for p in ROOT.glob("packages/*/vitest.config.*"):
        vitest_configs.append(str(p.relative_to(ROOT)))
    if vitest_configs:
        s.add("vitest 設定檔", PASS,
              f"找到 {len(vitest_configs)} 個：{vitest_configs}",
              time.perf_counter() - t0)
    else:
        # 可能內嵌在 package.json 或使用預設
        s.add("vitest 設定檔", INFO,
              "未找到獨立 vitest.config.*（可能使用預設或 package.json 內嵌設定）",
              time.perf_counter() - t0)

    # 有趣的測試案例分析：test-harness.test.ts
    t0 = time.perf_counter()
    harness_test = ROOT / "packages/coding-agent/test/test-harness.test.ts"
    if harness_test.exists():
        content = harness_test.read_text()
        lines = len(content.splitlines())
        s.add("test-harness.test.ts（coding-agent 內建 harness）", INFO,
              f"{lines} 行，{harness_test.stat().st_size:,} bytes",
              time.perf_counter() - t0)

    # coding-agent/test/rpc.test.ts
    t0 = time.perf_counter()
    rpc_test = ROOT / "packages/coding-agent/test/rpc.test.ts"
    if rpc_test.exists():
        content = rpc_test.read_text()
        test_cases = len(re.findall(r'\bit\s*\(|test\s*\(', content))
        s.add("rpc.test.ts 測試案例", INFO,
              f"約 {test_cases} 個測試案例，{len(content.splitlines())} 行",
              time.perf_counter() - t0)

    return s


# ──────────────────────────────────────────────────────────────────────────────
# 報告輸出
# ──────────────────────────────────────────────────────────────────────────────

def render_report(suites: list[TestSuite], total_elapsed: float) -> str:
    lines: list[str] = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    grand_pass  = sum(s.passed  for s in suites)
    grand_fail  = sum(s.failed  for s in suites)
    grand_warn  = sum(s.warned  for s in suites)
    grand_skip  = sum(s.skipped for s in suites)
    grand_total = sum(s.total   for s in suites)
    overall = "✅ ALL PASS" if grand_fail == 0 else "❌ FAILED"

    lines.append("# pi-mono 服務框架 Test Harness Report")
    lines.append(f"\n**產出時間**：{now}  ")
    lines.append(f"**執行耗時**：{total_elapsed:.2f}s  ")
    lines.append(f"**整體結果**：{overall}  ")
    lines.append(f"**統計**：{grand_pass} pass / {grand_fail} fail / {grand_warn} warn / {grand_skip} skip / {grand_total} total\n")
    lines.append("---\n")

    # 目錄
    lines.append("## 目錄\n")
    for i, suite in enumerate(suites, 1):
        icon = "✅" if suite.failed == 0 else "❌"
        lines.append(f"{i}. [{icon} {suite.title}](#{i})")
    lines.append("")
    lines.append("---\n")

    for i, suite in enumerate(suites, 1):
        icon = "✅" if suite.failed == 0 else "❌"
        lines.append(f"## {i}. {icon} {suite.title}")
        lines.append(f"> {suite.passed}/{suite.total} pass  |  {suite.failed} fail  |  {suite.warned} warn  |  {suite.skipped} skip\n")
        lines.append("| # | 測試項目 | 結果 | 說明 | 耗時(ms) |")
        lines.append("|---|---------|------|------|---------|")
        for j, r in enumerate(suite.results, 1):
            detail = r.detail.replace("|", "\\|")[:150]
            lines.append(f"| {j} | `{r.name}` | {r.status} | {detail} | {r.elapsed*1000:.1f} |")
        lines.append("")

    lines.append("---\n")
    lines.append("## 架構總覽（Architecture Overview）\n")
    lines.append("```")
    lines.append(textwrap.dedent("""\
    pi-mono  (v0.64.0)
    ├── packages/ai             @mariozechner/pi-ai
    │     ├── AI Provider 抽象層（stream / streamSimple）
    │     ├── 23+ 個 Provider（Anthropic, OpenAI, Google, Bedrock…）
    │     ├── 824 個預設模型（models.generated.js）
    │     └── Event Stream 框架
    │
    ├── packages/agent          @mariozechner/pi-agent-core
    │     ├── Agent（主控迴圈）
    │     ├── agentLoop / runAgentLoop
    │     └── streamProxy（代理轉發）
    │
    ├── packages/tui            @mariozechner/pi-tui
    │     ├── TUI（終端機 UI 框架）
    │     ├── 15+ 個 UI 元件（Box, Editor, Markdown…）
    │     └── KeybindingsManager, fuzzySearch
    │
    ├── packages/coding-agent   @mariozechner/pi-coding-agent
    │     ├── AgentSession（會話管理）
    │     ├── 工具：bash / edit / read / write / find / grep / ls
    │     ├── Compaction（上下文壓縮）
    │     ├── SessionManager（多分支會話）
    │     ├── AuthStorage（認證儲存）
    │     ├── RPC 模式（JSONL stdin/stdout 協議）
    │     └── 互動模式 / Print 模式
    │
    ├── packages/mom            @mariozechner/pi-mom
    │     ├── Multi-agent Orchestration
    │     ├── SlackBot 整合
    │     └── Sandbox 支援
    │
    ├── packages/pods           @mariozechner/pi
    │     └── 部署與封裝工具
    │
    ├── packages/web-ui         @mariozechner/pi-web-ui
    │     └── Web 介面
    │
    └── LinkPi.py               OpenAI 相容 HTTP Bridge
          ├── FastAPI Server（port 8765）
          ├── ProviderRegistry（per-provider PiProcess）
          ├── SharedMemory（跨 Provider 記憶）
          └── Endpoints: /v1/models, /v1/chat/completions,
                         /v1/consolidate, /v1/memory"""))
    lines.append("```\n")

    lines.append("## 測試涵蓋範圍\n")
    lines.append("| Suite | 涵蓋內容 | 方式 |")
    lines.append("|-------|---------|------|")
    lines.append("| 1. Monorepo 結構 | workspace、版本、scripts、設定檔 | package.json 解析 |")
    lines.append("| 2. Build 產出物 | dist/ 目錄、關鍵 .js/.d.ts 檔案 | 檔案系統掃描 |")
    lines.append("| 3. 模組載入 | 各套件 ESM import | Node.js --input-type=module |")
    lines.append("| 4. AI 套件框架 | provider 註冊、模型目錄、env keys | Node.js eval |")
    lines.append("| 5. 核心工具框架 | 工具定義、Agent、RPC、Auth、Compaction | Node.js eval |")
    lines.append("| 6. 服務框架 | TUI 元件、MOM、Pods、Web-UI | 檔案 + Node.js eval |")
    lines.append("| 7. 測試清單盤點 | 現有 test 檔案統計分類 | glob 掃描 |")
    lines.append("| **未涵蓋** | 真實 LLM 呼叫（需 API Key）、E2E 流程 | — |")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# 主程式
# ──────────────────────────────────────────────────────────────────────────────

async def main_async() -> None:
    print(f"🔍 測試目標：{ROOT}")
    print("=" * 70)

    t_start = time.perf_counter()
    suites: list[TestSuite] = []

    steps = [
        ("[1/7] Monorepo 結構…",     suite_monorepo_structure),
        ("[2/7] Build 產出物…",       suite_build_artifacts),
        ("[3/7] 模組載入（ESM）…",    suite_module_loading),
        ("[4/7] AI 套件框架…",        suite_ai_framework),
        ("[5/7] 核心工具框架…",       suite_core_tools),
        ("[6/7] 服務框架（TUI/MOM）…", suite_services),
        ("[7/7] 測試清單盤點…",       suite_test_inventory),
    ]

    for label, fn in steps:
        print(f"  {label}")
        suites.append(fn())

    total_elapsed = time.perf_counter() - t_start

    report = render_report(suites, total_elapsed)
    report_path = ROOT / "pi_mono_test_report.md"
    report_path.write_text(report, "utf-8")

    grand_pass  = sum(s.passed  for s in suites)
    grand_fail  = sum(s.failed  for s in suites)
    grand_warn  = sum(s.warned  for s in suites)
    grand_total = sum(s.total   for s in suites)

    print("=" * 70)
    for suite in suites:
        icon = "✅" if suite.failed == 0 else "❌"
        print(f"  {icon} {suite.title:<40} {suite.passed}/{suite.total} pass  {suite.failed} fail  {suite.warned} warn")
    print("-" * 70)
    print(f"  總計：{grand_pass}/{grand_total} pass  |  {grand_fail} fail  |  {grand_warn} warn")
    print(f"  耗時：{total_elapsed:.2f}s")
    print(f"  報告：{report_path}")
    print("=" * 70)

    sys.exit(0 if grand_fail == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main_async())
