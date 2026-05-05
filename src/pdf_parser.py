import io

import pdfplumber


def extract_text(pdf_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages)


def combine_pdfs_to_text(pdf_list: list[tuple[str, bytes]]) -> str:
    """複数PDFのテキストをファイル名ヘッダー付きで時系列順に結合する。"""
    lines = []
    for name, data in pdf_list:
        lines.append(f"=== {name} ===")
        lines.append(extract_text(data))
        lines.append("")
    return "\n".join(lines)
