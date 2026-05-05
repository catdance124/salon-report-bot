import asyncio

from notebooklm import NotebookLMClient

from config import ANALYSIS_QUERY, NOTEBOOK_TITLE


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
