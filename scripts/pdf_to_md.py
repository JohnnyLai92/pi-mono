"""
pdf_to_md.py — 將 iPAS 目錄下所有 PDF 轉換為 Markdown 檔案

用法：
  python scripts/pdf_to_md.py
  python scripts/pdf_to_md.py --dir path/to/pdf/dir
"""

import argparse
import re
import sys
from pathlib import Path

import fitz  # pymupdf


# 字型大小 → Markdown 標題層級（依實際 PDF 字型分析）
#   ≥ 45pt : # H1 — 章節大標（如「自然語言處理技術與應用」）
#   ≥ 28pt : ## H2 — 子章節標（如「前言與章節導覽」）
#   ≥ 18pt : ### H3 — 小節或表格群組標頭
#   < 18pt : 正文（含序文 14pt、內文 12pt、條列編號 13.6pt）
_HEADING_LEVELS = [
    (45.0, "# "),
    (28.0, "## "),
    (18.0, "### "),
]
_BODY_MIN    = 9.0    # 小於此值略過（頁碼、浮水印）
_BODY_MAX_H  = 17.9   # 小於此 size 視為正文


def _size_to_prefix(size: float) -> str:
    for threshold, prefix in _HEADING_LEVELS:
        if size >= threshold:
            return prefix
    return ""


def _clean(text: str) -> str:
    # 移除 Private Use Area 符號（PDF 裝飾字元，如  ）
    text = re.sub(r"[-]", "", text)
    text = text.replace(" ", " ")        # NBSP → space
    text = re.sub(r"[ \t]+", " ", text)       # 多餘空白合併
    return text.strip()


def _is_toc_line(text: str) -> bool:
    """目錄虛線行（....... 1-1 之類）"""
    return bool(re.search(r"\.{5,}.*\d", text) or re.search(r"\d-\d+\s*$", text))


def pdf_to_markdown(pdf_path: Path) -> str:
    doc = fitz.open(pdf_path)
    out: list[str] = []
    para_buf: list[str] = []   # 正文段落緩衝，換行前先累積

    def _flush_para():
        if para_buf:
            out.append(" ".join(para_buf))
            para_buf.clear()

    prev_prefix = ""

    for page_num in range(doc.page_count):
        page = doc[page_num]
        blocks = page.get_text("dict", sort=True)["blocks"]

        for block in blocks:
            if block["type"] != 0:
                continue

            for line in block["lines"]:
                spans = [s for s in line["spans"] if s["text"].strip()]
                if not spans:
                    continue

                max_size = max(s["size"] for s in spans)
                if max_size < _BODY_MIN:
                    continue

                text = _clean("".join(s["text"] for s in spans))
                if not text:
                    continue

                # 跳過目錄虛線行
                if _is_toc_line(text):
                    continue

                prefix = _size_to_prefix(max_size)

                if prefix:
                    # 標題前先把正文緩衝輸出
                    _flush_para()
                    if out and out[-1] != "":
                        out.append("")
                    out.append(f"{prefix}{text}")
                    out.append("")
                else:
                    # 正文：判斷是否接續上一段
                    if para_buf:
                        last = para_buf[-1]
                        # 上一句以句末標點結尾 → 新段落
                        if re.search(r"[。！？.!?」』)\]]$", last):
                            _flush_para()
                            out.append("")
                    para_buf.append(text)

                prev_prefix = prefix

    _flush_para()
    doc.close()

    result = "\n".join(out)
    # 壓縮連續空行
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def convert_dir(pdf_dir: Path) -> None:
    pdfs = sorted(pdf_dir.glob("*.pdf"))
    if not pdfs:
        print(f"找不到 PDF 檔案：{pdf_dir}")
        sys.exit(1)

    for pdf_path in pdfs:
        md_path = pdf_path.with_suffix(".md")
        print(f"轉換中：{pdf_path.name}")
        md_content = pdf_to_markdown(pdf_path)
        md_path.write_text(md_content, encoding="utf-8")
        print(f"  → {md_path.name}（{len(md_content):,} 字元）")


def main() -> None:
    parser = argparse.ArgumentParser(description="將目錄下所有 PDF 轉為 Markdown")
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path(__file__).parent.parent / "iPAS",
        help="PDF 所在目錄（預設：../iPAS）",
    )
    args = parser.parse_args()
    convert_dir(args.dir)


if __name__ == "__main__":
    main()
