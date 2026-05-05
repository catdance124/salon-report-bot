import json
from datetime import date
from pathlib import Path

STATE_FILE = Path(__file__).parent.parent / "state.json"
INTERVAL_DAYS = 5


def should_run() -> bool:
    if not STATE_FILE.exists():
        return True
    state = json.loads(STATE_FILE.read_text())
    last_run = date.fromisoformat(state["last_run"])
    return (date.today() - last_run).days >= INTERVAL_DAYS


def update_last_run() -> None:
    STATE_FILE.write_text(json.dumps({"last_run": date.today().isoformat()}))
