# salon-report-bot

ホットペッパービューティの管理サイト（サロンボード）からダウンロードしたサロンレポートPDFを解析し、経営状況のサマリーをLINE Worksに自動送信するBotです。

## 概要

1. Google Driveの指定フォルダから直近のサロンレポートPDF（日次保存分）を取得
2. 連続するPDF間の差分テキストを生成
3. NotebookLMに差分データを投入し、経営状況の分析・改善提案を生成
4. 分析結果をLINE Worksのチャンネルに送信
5. 上記を5日に1回のペースで実行

## ディレクトリ構成

```
salon-report-bot/
├── src/                    # ソースコード
│   ├── main.py             # エントリーポイント
│   ├── drive_client.py     # Google Drive連携
│   ├── lineworks_client.py # LINE Works Bot API連携
│   ├── notebooklm_client.py# NotebookLM連携
│   ├── pdf_parser.py       # PDFテキスト抽出・差分生成
│   └── scheduler.py        # 実行間隔管理
├── credentials/            # 認証情報（Gitignore済み）
│   ├── gdrive-service-account.json
│   └── lineworks-private.key
├── logs/                   # ログ出力先（Gitignore済み）
├── .env                    # 環境変数（Gitignore済み）
├── .env.example            # 環境変数テンプレート
├── pyproject.toml
└── uv.lock
```

## セットアップ

### 1. 依存関係のインストール

```bash
uv sync
```

### 2. 認証情報の配置

- `credentials/gdrive-service-account.json` — Google DriveアクセスのサービスアカウントキーJSON
- `credentials/lineworks-private.key` — LINE Works Bot APIのRSA秘密鍵

### 3. 環境変数の設定

`.env.example` をコピーして `.env` を作成し、各値を設定します。

```bash
cp .env.example .env
```

| 変数名 | 説明 |
|--------|------|
| `GDRIVE_SERVICE_ACCOUNT_JSON` | サービスアカウントJSONのパス |
| `GDRIVE_FOLDER_ID` | PDFが保存されているGoogle DriveフォルダのID |
| `LINEWORKS_CLIENT_ID` | LINE Works アプリのClient ID |
| `LINEWORKS_CLIENT_SECRET` | LINE Works アプリのClient Secret |
| `LINEWORKS_SERVICE_ACCOUNT_ID` | LINE Works サービスアカウントID |
| `LINEWORKS_PRIVATE_KEY_PATH` | RSA秘密鍵ファイルのパス |
| `LINEWORKS_BOT_ID` | LINE Works BotのID |
| `LINEWORKS_CHANNEL_ID` | 送信先チャンネル（またはユーザー）のID |

### 4. NotebookLMの認証

初回はブラウザでGoogleアカウントにサインインが必要です。

```bash
uv run notebooklm login
```

## 実行

```bash
uv run python src/main.py
```

前回実行から5日未満の場合はスキップされます。強制実行したい場合は `state.json` を削除してください。

## 外部サービスの準備

### Google Drive

1. Google Cloud ConsoleでサービスアカウントとDrive API v3を有効化
2. サービスアカウントのJSONキーを発行し `credentials/` に配置
3. 対象フォルダをサービスアカウントのメールアドレスに共有

### LINE Works Bot API

1. LINE Works Developer ConsoleでBot・アプリを作成
2. サービスアカウントとRSA鍵ペアを発行
3. Botを送信先チャンネルに招待
