from pathlib import Path

import yaml

_CONFIG_FILE = Path(__file__).parent.parent / "config.yml"
_config = yaml.safe_load(_CONFIG_FILE.read_text())

PDF_FETCH_COUNT: int = _config["drive"]["pdf_fetch_count"]
NOTEBOOK_TITLE: str = _config["notebooklm"]["notebook_title"]
KEEP_NOTEBOOK: bool = _config["notebooklm"]["keep_notebook"]
ANALYSIS_QUERY: str = _config["notebooklm"]["flex_message"]["query"].strip()
_video = _config["notebooklm"]["video"]
VIDEO_LANGUAGE: str = _video["language"]
VIDEO_FORMAT: str = _video["format"]
VIDEO_STYLE: str = _video["style"]
VIDEO_TIMEOUT: int = _video["timeout_seconds"]
VIDEO_INSTRUCTIONS: str | None = _video.get("instructions") or None

_extra_reference_urls_path = Path(__file__).parent.parent / _config["notebooklm"]["extra_reference_urls_file"]
EXTRA_REFERENCE_URLS: list[str] = (
    [line.strip() for line in _extra_reference_urls_path.read_text().splitlines() if line.strip() and not line.startswith("#")]
    if _extra_reference_urls_path.exists()
    else []
)
