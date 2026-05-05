import io
from datetime import date

import pdfplumber


def extract_text(pdf_bytes: bytes) -> str:
    """PDFバイト列からテキストを抽出する。"""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages)


def compute_diffs(pdf_list: list[tuple[str, bytes]]) -> list[dict]:
    """連続するPDF間の差分を日次データとして返す。

    Args:
        pdf_list: (filename, pdf_bytes) のリスト（古い順）

    Returns:
        各日の差分情報を含むdictのリスト
        [{"date": "2026-05-01", "prev_file": "...", "curr_file": "...", "text_diff": "..."}]
    """
    if len(pdf_list) < 2:
        return []

    diffs = []
    texts = [(name, extract_text(data)) for name, data in pdf_list]

    for i in range(1, len(texts)):
        prev_name, prev_text = texts[i - 1]
        curr_name, curr_text = texts[i]
        diff_entry = {
            "prev_file": prev_name,
            "curr_file": curr_name,
            "prev_text": prev_text,
            "curr_text": curr_text,
        }
        diffs.append(diff_entry)
    return diffs


def format_diffs_for_analysis(diffs: list[dict]) -> str:
    """差分データをNotebookLMへの入力テキストに整形する。"""
    lines = []
    for i, d in enumerate(diffs, 1):
        lines.append(f"=== 日次変化 {i}日目 ({d['prev_file']} → {d['curr_file']}) ===")
        lines.append("[前日データ]")
        lines.append(d["prev_text"])
        lines.append("[当日データ]")
        lines.append(d["curr_text"])
        lines.append("")
    return "\n".join(lines)
