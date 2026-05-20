import io
import os
from pathlib import Path

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
SERVICE_ACCOUNT_FILE = os.environ["GDRIVE_SERVICE_ACCOUNT_JSON"]
FOLDER_ID = os.environ["GDRIVE_FOLDER_ID"]


def _get_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


def fetch_recent_pdfs(n: int = 7) -> list[tuple[str, bytes]]:
    """Google DriveフォルダからPDFをファイル名順に直近n件取得する。

    Returns:
        (filename, pdf_bytes) のリスト（古い順）
    """
    service = _get_service()
    query = f"'{FOLDER_ID}' in parents and mimeType='application/pdf' and trashed=false"
    results = (
        service.files()
        .list(
            q=query,
            orderBy="name desc",
            fields="files(id, name)",
            pageSize=n,
        )
        .execute()
    )
    files = results.get("files", [])
    if not files:
        return []

    recent = list(reversed(files))
    pdfs: list[tuple[str, bytes]] = []
    for f in recent:
        buf = io.BytesIO()
        request = service.files().get_media(fileId=f["id"])
        downloader = MediaIoBaseDownload(buf, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        pdfs.append((f["name"], buf.getvalue()))
    return pdfs
