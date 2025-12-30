# Brain Wave Paper Notification Bot

arXivとElsevier（Scopus）から「脳波（brain waves/EEG）」に関する最新の論文を自動取得し、ローカルLLM（LM Studio）で要約・翻訳した内容をDiscordに通知するボットです。

## 特徴

- **マルチソース対応**: arXivとElsevier Scopus APIから新着論文を収集。
- **インテリジェントな要約**: LM Studio（OpenAI互換API）を使用して、論文の内容を日本語で分かりやすく要約・翻訳。
- **スマートなフィルタリング**:
    - 公開日時ベースのフィルタリングにより、前回の確認以降の新着のみを取得。
    - 送信済み論文のIDを記録し、重複通知を防止。
- **充実した通知内容**:
    - APA形式の引用を自動生成。
    - DOIおよび論文ソースへの直接リンクを表示。
- **プライバシー配慮**: 思考プロセス（`<think>`タグ）を自動的に除去して通知。

## セットアップ

### 1. 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

### 2. 環境設定

`.env.example` を `.env` にコピーし、必要な情報を入力してください。

```bash
cp .env.example .env
```

- `DISCORD_WEBHOOK_URL`: 通知を送信するDiscordのウェブフックURL
- `ELSEVIER_API_KEY`: Elsevier開発者ポータルで取得したAPIキー

### 3. LM Studio の準備

- LM Studioを起動し、Local Serverを開始してください。
- デフォルトのポート（1234）を使用するか、`config.py` でポートを変更してください。

## 使い方

以下のコマンドを実行すると、常駐モード（デフォルト30分おき）で論文の取得と通知を開始します。

```bash
python3 main.py
```

## 設定のカスタマイズ

`config.py` 内の以下の項目を変更することで、挙動をカスタマイズできます。

- `SEARCH_QUERY`: 検索キーワード
- `FETCH_INTERVAL_SECONDS`: 更新間隔（秒）
- `LM_STUDIO_BASE_URL`: LM StudioのサーバーURL
- `LM_STUDIO_MODEL`: 使用するモデル名（通常は自動で認識されます）

## 免責事項

APIの利用規約に従ってご利用ください。特に短時間での頻繁なアクセスはAPI制限の原因となる可能性があります。
