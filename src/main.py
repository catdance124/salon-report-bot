import argparse
import logging
import sys
from pathlib import Path

from config import INTERVAL_DAYS, PDF_FETCH_COUNT
from drive_client import fetch_recent_pdfs
from lineworks_client import send_flex_message
from notebooklm_client import analyze_with_notebooklm
from pdf_parser import combine_pdfs_to_text
from scheduler import should_run, update_last_run

_LOG_DIR = Path(__file__).parent.parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(_LOG_DIR / "salon-report-bot.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


def run(force: bool = False) -> None:
    if not force and not should_run():
        log.info(f"前回実行から{INTERVAL_DAYS}日未満のためスキップします")
        return

    log.info("サロンレポートBot 実行開始")

    log.info("Google DriveからPDFを取得中...")
    pdfs = fetch_recent_pdfs(n=PDF_FETCH_COUNT)
    if len(pdfs) < 2:
        log.warning("PDFが2件未満のため処理をスキップします")
        return

    log.info(f"{len(pdfs)}件のPDFを取得、テキストを結合中...")
    analysis_text = combine_pdfs_to_text(pdfs)

    log.info("NotebookLMで分析中...")
    analysis_data = analyze_with_notebooklm(analysis_text)

    period_start = pdfs[0][0]
    period_end = pdfs[-1][0]

    log.info("LINE Worksに送信中...")
    send_flex_message(analysis_data, period_start, period_end)

    update_last_run()
    log.info("完了しました")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="サロンレポートBot")
    parser.add_argument(
        "--force",
        action="store_true",
        help="実行間隔チェックをスキップして強制実行する",
    )
    args = parser.parse_args()
    run(force=args.force)
