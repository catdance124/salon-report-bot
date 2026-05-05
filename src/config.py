from pathlib import Path

import yaml

_CONFIG_FILE = Path(__file__).parent.parent / "config.yml"
_config = yaml.safe_load(_CONFIG_FILE.read_text())

INTERVAL_DAYS: int = _config["scheduler"]["interval_days"]
PDF_FETCH_COUNT: int = _config["drive"]["pdf_fetch_count"]
NOTEBOOK_TITLE: str = _config["notebooklm"]["notebook_title"]
ANALYSIS_QUERY: str = _config["notebooklm"]["analysis_query"].strip()
