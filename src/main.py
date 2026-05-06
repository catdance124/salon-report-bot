import argparse
import logging
import sys
from pathlib import Path

from config import PDF_FETCH_COUNT
from drive_client import fetch_recent_pdfs
from lineworks_client import send_flex_message, send_video_message
from notebooklm_client import (
    analyze_and_generate_video_with_notebooklm,
    analyze_with_notebooklm,
    generate_video_with_notebooklm,
)
from pdf_parser import combine_pdfs_to_text

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


def run(mode: str = "flex_message") -> None:
    log.info("サロンレポートBot 実行開始（mode=%s）", mode)

    log.info("Google DriveからPDFを取得中...")
    pdfs = fetch_recent_pdfs(n=PDF_FETCH_COUNT)
    if len(pdfs) < 2:
        log.warning("PDFが2件未満のため処理をスキップします")
        return

    log.info(f"{len(pdfs)}件のPDFを取得、テキストを結合中...")
    analysis_text = combine_pdfs_to_text(pdfs)

    period_start = pdfs[0][0]
    period_end = pdfs[-1][0]

    analysis_data: dict | None = None
    video_path: str | None = None

    if mode == "flex_message":
        log.info("NotebookLMで分析中...")
        analysis_data = analyze_with_notebooklm(analysis_text)
    elif mode == "video":
        log.info("NotebookLMで動画生成中...")
        video_path = generate_video_with_notebooklm(analysis_text)
    else:  # both
        log.info("NotebookLMで分析・動画生成中...")
        analysis_data, video_path = analyze_and_generate_video_with_notebooklm(analysis_text)

    if analysis_data is not None:
        log.info("LINE WorksにFlexメッセージを送信中...")
        send_flex_message(analysis_data, period_start, period_end)

    if video_path is not None:
        log.info("LINE Worksに動画を送信中...")
        send_video_message(video_path)
    elif mode in ("video", "both"):
        log.warning("動画生成に失敗したためスキップします")

    log.info("完了しました")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="サロンレポートBot")
    parser.add_argument(
        "--mode",
        choices=["flex_message", "video", "both"],
        default="flex_message",
        help="送信モード: flex_message（分析レポートのみ）/ video（動画のみ）/ both（両方）",
    )
    args = parser.parse_args()
    run(mode=args.mode)
