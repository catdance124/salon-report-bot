import os

from notebooklm import NotebookLM

NOTEBOOK_TITLE = "サロンレポート分析"
ANALYSIS_QUERY = (
    "直近の経営状況を分析してください。"
    "売上・予約数・客単価の推移、好調な点と改善が必要な点を具体的にまとめてください。"
    "経営者が翌日から行動できるような実践的な改善提案も含めてください。"
)


def analyze_with_notebooklm(analysis_text: str) -> str:
    """差分テキストをNotebookLMに送り経営サマリーを取得する。

    Args:
        analysis_text: format_diffs_for_analysis() で生成した文字列

    Returns:
        NotebookLMが生成した分析テキスト
    """
    client = NotebookLM()

    notebook = client.create_notebook(title=NOTEBOOK_TITLE)
    try:
        notebook.add_source(text=analysis_text, title="サロンレポート差分データ")
        response = notebook.chat(ANALYSIS_QUERY)
        return response.text
    finally:
        notebook.delete()
