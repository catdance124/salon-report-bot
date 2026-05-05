"""テストデータでFlexメッセージのHTMLプレビューを生成する。"""
import pathlib

TEST_DATA = {
    "summary": (
        "先週は新規顧客の獲得が好調で、リピート率も前週比＋5%と改善しました。"
        "スタッフの技術力向上が売上増加に直結しており、引き続き研修への投資が重要です。"
    ),
    "metrics": [
        {"label": "売上",       "value": "¥480,000", "trend": "前週比 ＋8%"},
        {"label": "来客数",     "value": "62名",      "trend": "前週比 ＋4名"},
        {"label": "新規顧客数", "value": "18名",      "trend": "前週比 ＋3名"},
        {"label": "リピート率", "value": "71%",       "trend": "前週比 ＋5pt"},
        {"label": "客単価",     "value": "¥7,742",    "trend": "前週比 ＋¥280"},
    ],
    "highlights": [
        "新規顧客獲得数が月間目標の60%を1週間で達成",
        "カラーメニューの売上が全体の45%を占め過去最高を更新",
        "口コミ評価4.8を維持し高水準をキープ",
    ],
    "improvements": [
        "火曜・水曜の稼働率が50%以下と低く、平日集客策が必要",
        "指名なし新規の再来率が40%にとどまり、カウンセリング強化が課題",
    ],
    "actions": [
        "平日限定クーポンをHot Pepper Beautyに掲載（月・火・水対象）",
        "初回来店客へのサンキューメッセージ送信フローを整備",
        "スタッフ全員で週次ロールプレイ研修を実施（木曜朝）",
    ],
}

PERIOD_START = "2025-04-28"
PERIOD_END   = "2025-05-04"

CARD_STYLE = """
    .card {
        background: #fff;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        width: 260px;
        flex-shrink: 0;
        overflow: hidden;
        font-family: -apple-system, 'Hiragino Sans', 'Hiragino Kaku Gothic ProN', Meiryo, sans-serif;
        font-size: 13px;
    }
    .card-header {
        padding: 10px 14px;
        color: #fff;
        font-weight: bold;
        font-size: 13px;
    }
    .card-body {
        padding: 12px 14px;
        line-height: 1.6;
    }
    .separator {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 8px 0;
    }
    .period {
        font-size: 11px;
        color: #888;
        margin-bottom: 6px;
    }
    .metric-block {
        margin-bottom: 8px;
    }
    .metric-label {
        font-size: 11px;
        color: #6b7280;
    }
    .metric-row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
    }
    .metric-value {
        font-weight: bold;
    }
    .metric-trend {
        font-size: 11px;
        color: #6b7280;
        text-align: right;
    }
    .section-title {
        font-weight: bold;
        margin-top: 6px;
        margin-bottom: 4px;
    }
    .bullet {
        margin: 2px 0;
    }
"""


def _card(header_color: str, title: str, body_html: str) -> str:
    return f"""
    <div class="card">
        <div class="card-header" style="background:{header_color};">{title}</div>
        <div class="card-body">{body_html}</div>
    </div>"""


def _card_summary(data: dict, period_start: str, period_end: str) -> str:
    body = (
        f'<div class="period">{period_start} → {period_end}</div>'
        f'<hr class="separator">'
        f'<div>{data.get("summary", "")}</div>'
    )
    return _card("#3b82f6", "📊 概要", body)


def _card_metrics(data: dict) -> str:
    rows = ""
    for m in data.get("metrics", []):
        rows += (
            f'<div class="metric-block">'
            f'<div class="metric-label">{m["label"]}</div>'
            f'<div class="metric-row">'
            f'<span class="metric-value">{m["value"]}</span>'
            f'<span class="metric-trend">{m["trend"]}</span>'
            f'</div></div>'
        )
    return _card("#10b981", "📈 数値推移", rows or "データなし")


def _card_eval(data: dict) -> str:
    highlights = "".join(
        f'<div class="bullet">・{h}</div>' for h in data.get("highlights", [])
    )
    improvements = "".join(
        f'<div class="bullet">・{i}</div>' for i in data.get("improvements", [])
    )
    body = (
        f'<div class="section-title">✅ 好調な点</div>{highlights}'
        f'<hr class="separator">'
        f'<div class="section-title">⚠️ 改善が必要な点</div>{improvements}'
    )
    return _card("#f59e0b", "🔍 評価", body)


def _card_actions(data: dict) -> str:
    items = "".join(
        f'<div class="bullet">・{a}</div>' for a in data.get("actions", [])
    )
    return _card("#ef4444", "🚀 今週のアクション", items or "データなし")


def generate_html(data: dict, period_start: str, period_end: str) -> str:
    cards = (
        _card_summary(data, period_start, period_end)
        + _card_metrics(data)
        + _card_eval(data)
        + _card_actions(data)
    )
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Flex Message プレビュー</title>
<style>
body {{
    background: #e5e7eb;
    margin: 0;
    padding: 24px;
}}
.carousel {{
    display: flex;
    gap: 12px;
    overflow-x: auto;
    padding-bottom: 8px;
}}
{CARD_STYLE}
</style>
</head>
<body>
<div class="carousel">
{cards}
</div>
</body>
</html>"""


if __name__ == "__main__":
    html = generate_html(TEST_DATA, PERIOD_START, PERIOD_END)
    out = pathlib.Path(__file__).parent.parent / "preview.html"
    out.write_text(html, encoding="utf-8")
    print(f"生成完了: {out}")
