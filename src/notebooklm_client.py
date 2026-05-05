import asyncio
import json
import logging
import re

from notebooklm import NotebookLMClient

from config import ANALYSIS_QUERY, NOTEBOOK_TITLE

log = logging.getLogger(__name__)


def _parse_json(text: str) -> dict:
    # マークダウンのコードブロックを除去
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1)
    # JSON オブジェクト部分を抽出
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        text = match.group(0)
    return json.loads(text)


async def _analyze(analysis_text: str) -> dict:
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
            log.debug("NotebookLM raw response: %s", result.answer)
            return _parse_json(result.answer)
        finally:
            await client.notebooks.delete(notebook.id)


def analyze_with_notebooklm(analysis_text: str) -> dict:
    return asyncio.run(_analyze(analysis_text))
