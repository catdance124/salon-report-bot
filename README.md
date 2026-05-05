# salon-report-bot

ホットペッパービューティの管理サイト（サロンボード）からダウンロードしたサロンレポートPDFを解析し、経営状況のサマリーをLINE Worksに自動送信するBotです。

## 概要

1. Google Driveの指定フォルダから直近のサロンレポートPDF（日次保存分）を取得
2. 複数PDFのテキストを結合
3. NotebookLMに投入し、経営状況の分析・改善提案を生成
4. 分析結果をLINE Worksのチャンネルに送信

## ディレクトリ構成

```
salon-report-bot/
├── src/                    # ソースコード
│   ├── main.py             # エントリーポイント
│   ├── config.py           # 設定ローダー
│   ├── drive_client.py     # Google Drive連携
│   ├── lineworks_client.py # LINE Works Bot API連携
│   ├── notebooklm_client.py# NotebookLM連携
│   └── pdf_parser.py       # PDFテキスト抽出
├── credentials/            # 認証情報（Gitignore済み）
│   ├── gdrive-service-account.json
│   └── lineworks-private.key
├── logs/                   # ログ出力先（Gitignore済み）
├── config.yml              # 非秘匿設定
├── extra_reference_urls.txt# NotebookLMに追加する参照URL（Gitignore済み・任意）
├── .env                    # 秘匿情報（Gitignore済み）
├── .env.example            # 秘匿情報テンプレート
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

### 3. 秘匿情報の設定

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

### 4. 動作設定の変更（任意）

`config.yml` で各種設定を変更できます。

| キー | デフォルト | 説明 |
|------|-----------|------|
| `drive.pdf_fetch_count` | `7` | Google Driveから取得するPDF件数 |
| `notebooklm.notebook_title` | `"サロンレポート分析"` | NotebookLMノートブック名 |
| `notebooklm.extra_reference_urls_file` | `"extra_reference_urls.txt"` | 追加参照URLファイルのパス |
| `notebooklm.analysis_query` | （省略） | NotebookLMへの分析クエリ |

### 5. 追加参照URLの設定（任意）

NotebookLMのソースとして、サロンレポートPDF以外のURLを追加したい場合は `extra_reference_urls.txt` を作成します。このファイルはGitignore対象のため、サロン固有のURLをコミットせずに管理できます。

```
# extra_reference_urls.txt
# 1行1URL。# から始まる行はコメント。
https://beauty.hotpepper.jp/kr/example
https://beauty.hotpepper.jp/kr/example/coupon/
https://beauty.hotpepper.jp/kr/example/review/
#https://beauty.hotpepper.jp/kr/example/map/
```

ファイルが存在しない場合は何も追加されません。ファイルのパスは `config.yml` の `notebooklm.extra_reference_urls_file` で変更できます。

### 6. NotebookLMの認証

初回はブラウザでGoogleアカウントにサインインが必要です。

```bash
uv run notebooklm login
```

## 実行

```bash
uv run python src/main.py
```

## 外部サービスの準備

### Google Drive

1. Google Cloud ConsoleでサービスアカウントとDrive API v3を有効化
2. サービスアカウントのJSONキーを発行し `credentials/` に配置
3. 対象フォルダをサービスアカウントのメールアドレスに共有

### LINE Works Bot API

1. LINE Works Developer ConsoleでBot・アプリを作成
2. サービスアカウントとRSA鍵ペアを発行
3. Botを送信先チャンネルに招待
