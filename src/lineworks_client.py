import os
import time
from pathlib import Path

import jwt
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ["LINEWORKS_CLIENT_ID"]
CLIENT_SECRET = os.environ["LINEWORKS_CLIENT_SECRET"]
SERVICE_ACCOUNT_ID = os.environ["LINEWORKS_SERVICE_ACCOUNT_ID"]
PRIVATE_KEY_PATH = os.environ["LINEWORKS_PRIVATE_KEY_PATH"]
BOT_ID = os.environ["LINEWORKS_BOT_ID"]
CHANNEL_ID = os.environ["LINEWORKS_CHANNEL_ID"]

TOKEN_URL = "https://auth.worksmobile.com/oauth2/v2.0/token"
API_BASE = "https://www.worksapis.com/v1.0"


def _get_access_token() -> str:
    private_key = Path(PRIVATE_KEY_PATH).read_text()
    now = int(time.time())
    payload = {
        "iss": CLIENT_ID,
        "sub": SERVICE_ACCOUNT_ID,
        "iat": now,
        "exp": now + 3600,
    }
    assertion = jwt.encode(payload, private_key, algorithm="RS256")
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": "bot",
        },
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def send_message(text: str) -> None:
    """LINE Works のチャンネル（グループまたはユーザー）にテキストメッセージを送信する。"""
    token = _get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "content": {
            "type": "text",
            "text": text,
        }
    }
    url = f"{API_BASE}/bots/{BOT_ID}/channels/{CHANNEL_ID}/messages"
    resp = requests.post(url, json=payload, headers=headers)
    resp.raise_for_status()
