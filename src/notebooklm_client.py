import asyncio

from notebooklm import NotebookLMClient

NOTEBOOK_TITLE = "サロンレポート分析"
ANALYSIS_QUERY = (
    "直近の経営状況を分析してください。"
    "売上・予約数・客単価の推移、好調な点と改善が必要な点を具体的にまとめてください。"
    "経営者が翌日から行動できるような実践的な改善提案も含めてください。"
)


async def _analyze(analysis_text: str) -> str:
    async with await NotebookLMClient.from_storage() as client:
        notebook = await client.notebooks.create(title=NOTEBOOK_TITLE)
        try:
            await client.sources.add_text(
                notebook_id=notebook.id,
                title="サロンレポート差分データ",
                content=analysis_text,
                wait=True,
            )
            result = await client.chat.ask(
                notebook_id=notebook.id,
                question=ANALYSIS_QUERY,
            )
            return result.answer
        finally:
            await client.notebooks.delete(notebook.id)


def analyze_with_notebooklm(analysis_text: str) -> str:
    return asyncio.run(_analyze(analysis_text))
