import argparse
import logging
import sys

from config import INTERVAL_DAYS, PDF_FETCH_COUNT
from drive_client import fetch_recent_pdfs
from lineworks_client import send_message
from notebooklm_client import analyze_with_notebooklm
from pdf_parser import compute_diffs, format_diffs_for_analysis
from scheduler import should_run, update_last_run

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
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

    log.info(f"{len(pdfs)}件のPDFを取得、差分を計算中...")
    diffs = compute_diffs(pdfs)
    analysis_text = format_diffs_for_analysis(diffs)

    log.info("NotebookLMで分析中...")
    summary = analyze_with_notebooklm(analysis_text)

    period_start = pdfs[0][0]
    period_end = pdfs[-1][0]
    message = f"【サロン経営レポート {period_start} → {period_end}】\n\n{summary}"

    log.info("LINE Worksに送信中...")
    send_message(message)

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
