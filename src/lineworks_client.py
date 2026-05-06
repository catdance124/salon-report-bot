import logging
import os
import time
from datetime import date
from pathlib import Path

import jwt
import requests
from dotenv import load_dotenv

log = logging.getLogger(__name__)

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


def _post_message(content: dict) -> None:
    token = _get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    url = f"{API_BASE}/bots/{BOT_ID}/channels/{CHANNEL_ID}/messages"
    resp = requests.post(url, json={"content": content}, headers=headers)
    if not resp.ok:
        log.error("LINE Works APIエラー: status=%s body=%s", resp.status_code, resp.text)
    resp.raise_for_status()


def _header_box(title: str, bg_color: str) -> dict:
    return {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": bg_color,
        "paddingAll": "md",
        "contents": [
            {"type": "text", "text": title, "weight": "bold", "color": "#ffffff", "size": "sm"}
        ],
    }


def _bullet(text: str) -> dict:
    return {"type": "text", "text": f"・{text}", "wrap": True, "size": "sm"}


def _build_carousel(data: dict, period_start: str, period_end: str) -> dict:
    # Card 1: 概要
    card_summary = {
        "type": "bubble",
        "header": _header_box("📊 概要", "#3b82f6"),
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {"type": "text", "text": f"{period_start} → {period_end}", "size": "xs", "color": "#888888"},
                {"type": "separator"},
                {"type": "text", "text": data.get("summary", ""), "wrap": True, "size": "sm"},
            ],
        },
    }

    # Card 2: 数値推移
    metric_rows = []
    for m in data.get("metrics", []):
        metric_rows.append({
            "type": "box",
            "layout": "vertical",
            "spacing": "xs",
            "contents": [
                {"type": "text", "text": m.get("label", ""), "size": "xs", "color": "#6b7280"},
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": m.get("value", ""), "size": "sm", "weight": "bold", "flex": 1},
                        {"type": "text", "text": m.get("trend", ""), "size": "xs", "color": "#6b7280", "align": "end", "flex": 1, "wrap": True},
                    ],
                },
            ],
        })
    card_metrics = {
        "type": "bubble",
        "header": _header_box("📈 数値推移", "#10b981"),
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": metric_rows or [{"type": "text", "text": "データなし", "size": "sm"}],
        },
    }

    # Card 3: 評価（好調な点・改善点）
    eval_contents = [{"type": "text", "text": "✅ 好調な点", "weight": "bold", "size": "sm"}]
    eval_contents += [_bullet(h) for h in data.get("highlights", [])]
    eval_contents.append({"type": "separator", "margin": "md"})
    eval_contents.append({"type": "text", "text": "⚠️ 改善が必要な点", "weight": "bold", "size": "sm", "margin": "md"})
    eval_contents += [_bullet(i) for i in data.get("improvements", [])]
    card_eval = {
        "type": "bubble",
        "header": _header_box("🔍 評価", "#f59e0b"),
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "xs",
            "contents": eval_contents,
        },
    }

    # Card 4: 今週のアクション
    action_contents = [_bullet(a) for a in data.get("actions", [])]
    card_actions = {
        "type": "bubble",
        "header": _header_box("🚀 今週のアクション", "#ef4444"),
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "xs",
            "contents": action_contents or [{"type": "text", "text": "データなし", "size": "sm"}],
        },
    }

    return {
        "type": "flex",
        "altText": f"サロン経営レポート {period_start} → {period_end}",
        "contents": {
            "type": "carousel",
            "contents": [card_summary, card_metrics, card_eval, card_actions],
        },
    }


def _upload_file(file_path: str) -> str:
    """ファイルをLINE Worksにアップロードし、fileIdを返す。"""
    token = _get_access_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    file_name = f"{date.today()}.mp4"

    resp = requests.post(
        f"{API_BASE}/bots/{BOT_ID}/attachments",
        json={"fileName": file_name},
        headers=headers,
    )
    resp.raise_for_status()
    data = resp.json()
    upload_url: str = data["uploadUrl"]
    file_id: str = data["fileId"]

    upload_headers = {"Authorization": f"Bearer {token}"}
    with open(file_path, "rb") as f:
        upload_resp = requests.post(
            upload_url,
            headers=upload_headers,
            files={
                "FileData": (file_name, f, "video/mp4"),
                "resourceName": (None, file_name),
            },
        )
    if not upload_resp.ok:
        log.error("ファイルアップロードエラー: status=%s body=%s", upload_resp.status_code, upload_resp.text)
    upload_resp.raise_for_status()
    return file_id


def send_flex_message(data: dict, period_start: str, period_end: str) -> None:
    """LINE Works のチャンネルにFlexible Template（Carousel）で送信する。"""
    content = _build_carousel(data, period_start, period_end)
    _post_message(content)


def send_video_message(video_path: str) -> None:
    """動画ファイルをLINE Worksにアップロードして送信する。"""
    file_id = _upload_file(video_path)
    _post_message({"type": "file", "fileId": file_id})
