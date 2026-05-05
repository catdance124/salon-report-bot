import asyncio
import json
import logging
import os
import re
import tempfile
from datetime import datetime

from notebooklm import NotebookLMClient
from notebooklm.rpc import VideoFormat, VideoStyle

from config import ANALYSIS_QUERY, EXTRA_REFERENCE_URLS, KEEP_NOTEBOOK, NOTEBOOK_TITLE, VIDEO_FORMAT, VIDEO_LANGUAGE, VIDEO_STYLE, VIDEO_TIMEOUT

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


async def _run(
    analysis_text: str,
    need_analysis: bool,
    need_video: bool,
) -> tuple[dict | None, str | None]:
    async with await NotebookLMClient.from_storage() as client:
        title = f"{NOTEBOOK_TITLE} {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        notebook = await client.notebooks.create(title=title)
        try:
            await client.sources.add_text(
                notebook_id=notebook.id,
                title="サロンレポートデータ",
                content=analysis_text,
                wait=True,
            )

            if EXTRA_REFERENCE_URLS:
                log.info("参照URLを%d件追加します", len(EXTRA_REFERENCE_URLS))
                url_sources = [
                    await client.sources.add_url(notebook_id=notebook.id, url=url)
                    for url in EXTRA_REFERENCE_URLS
                ]
                await client.sources.wait_for_sources(
                    notebook.id, [s.id for s in url_sources]
                )

            analysis_data: dict | None = None
            if need_analysis:
                result = await client.chat.ask(
                    notebook_id=notebook.id,
                    question=ANALYSIS_QUERY,
                )
                log.debug("NotebookLM raw response: %s", result.answer)
                analysis_data = _parse_json(result.answer)

            video_path: str | None = None
            if need_video:
                log.info("動画生成を開始します（最大%d秒）", VIDEO_TIMEOUT)
                status = await client.artifacts.generate_video(
                    notebook.id,
                    language=VIDEO_LANGUAGE,
                    video_format=VideoFormat[VIDEO_FORMAT],
                    video_style=VideoStyle[VIDEO_STYLE],
                )
                if status.is_failed:
                    log.warning("動画生成の開始に失敗しました: %s", status.error)
                else:
                    final = await client.artifacts.wait_for_completion(
                        notebook.id,
                        status.task_id,
                        timeout=VIDEO_TIMEOUT,
                    )
                    if final.is_complete:
                        fd, tmp_path = tempfile.mkstemp(suffix=".mp4")
                        os.close(fd)
                        video_path = await client.artifacts.download_video(
                            notebook.id, tmp_path
                        )
                        log.info("動画をダウンロードしました: %s", video_path)
                    else:
                        log.warning("動画生成が完了しませんでした: %s", final.status)

            return analysis_data, video_path
        finally:
            if not KEEP_NOTEBOOK:
                await client.notebooks.delete(notebook.id)


def analyze_with_notebooklm(analysis_text: str) -> dict:
    data, _ = asyncio.run(_run(analysis_text, need_analysis=True, need_video=False))
    return data


def generate_video_with_notebooklm(analysis_text: str) -> str | None:
    _, path = asyncio.run(_run(analysis_text, need_analysis=False, need_video=True))
    return path


def analyze_and_generate_video_with_notebooklm(
    analysis_text: str,
) -> tuple[dict, str | None]:
    data, path = asyncio.run(_run(analysis_text, need_analysis=True, need_video=True))
    return data, path
