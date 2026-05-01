# Docker エンジニアガイド

このプロジェクトのDocker構成の設計意図・コマンド・クラウドデプロイまでをまとめたガイドです。

---

## ファイル構成

```
プロジェクトルート/
├── Dockerfile          # イメージの設計図
├── docker-compose.yml  # ローカル開発用の起動定義
├── .dockerignore       # イメージに含めないファイルの除外リスト
└── .env                # 環境変数（gitignore済み、各自で用意）
```

---

## Dockerfile の構造

```dockerfile
FROM python:3.12-slim          # ベースイメージ（軽量なDebian+Python）
WORKDIR /app                   # コンテナ内の作業ディレクトリ
COPY requirements.txt .        # 依存関係だけ先にコピー
RUN pip install ...            # キャッシュを活かすため COPY app/ より前に実行
COPY app/ ./app/               # アプリ本体
RUN mkdir -p data/snapshots    # データ保存ディレクトリを作成
EXPOSE 8000                    # ドキュメント用（実際の公開は compose で制御）
CMD ["uvicorn", ...]           # デフォルト起動コマンド
```

**なぜ requirements.txt を先にコピーするのか**
Dockerはレイヤーをキャッシュします。`requirements.txt` が変わらない限り `pip install` をスキップできるため、コードを変更するたびに毎回インストールが走らなくなります。

---

## docker-compose.yml の構造

```yaml
services:
  app:
    build: .              # このディレクトリの Dockerfile を使ってビルド
    ports:
      - "8000:8000"       # ホスト:コンテナ のポートマッピング
    env_file:
      - .env              # 環境変数ファイルを読み込む
    volumes:
      - ./data:/app/data  # data/ フォルダをコンテナと共有（データ永続化）
    restart: unless-stopped
```

**volumes について**
コンテナを削除してもホスト側の `./data/` は残ります。CSVとスナップショットはここに蓄積されます。

---

## 主要コマンド

```bash
# 起動（バックグラウンド）
docker compose up -d

# ログ確認
docker compose logs -f

# 停止
docker compose down

# イメージを再ビルドして起動（コードを変えたとき）
docker compose up -d --build

# コンテナ内に入る（デバッグ）
docker compose exec app bash

# イメージだけビルド（デプロイ前の確認）
docker build -t cut-in-meter .
```

---

## 環境変数一覧

| 変数名 | 必須 | デフォルト | 説明 |
|--------|------|-----------|------|
| `OPENAI_API_KEY` | ✅ | なし | OpenAI API キー |
| `OPENAI_MODEL` | | gpt-5.4-mini | 使用するモデル |
| `OPENAI_TIMEOUT_SEC` | | 30 | APIタイムアウト（秒） |
| `FRAME_INTERVAL_SEC` | | 5 | フレーム取得間隔 |
| `IMAGE_MAX_WIDTH` | | 1024 | 画像最大幅（px） |
| `IMAGE_JPEG_QUALITY` | | 0.75 | JPEG品質（0〜1） |

---

## クラウドへのデプロイ

### Fly.io（推奨：最速・無料枠あり）

```bash
# Fly CLI のインストール
brew install flyctl   # Mac
# Windows: https://fly.io/docs/getting-started/installing-flyctl/

# ログインと初期設定
fly auth login
fly launch           # Dockerfile を自動検出してセットアップ

# 環境変数を設定
fly secrets set OPENAI_API_KEY=your_key_here

# デプロイ
fly deploy
```

### Google Cloud Run

```bash
# イメージをビルドしてプッシュ
gcloud builds submit --tag gcr.io/YOUR_PROJECT/cut-in-meter

# デプロイ（スケールゼロ対応・従量課金）
gcloud run deploy cut-in-meter \
  --image gcr.io/YOUR_PROJECT/cut-in-meter \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your_key
```

> Cloud Run はコンテナが停止するとファイルが消えます。`data/` を永続化するには Cloud Storage や Cloud SQL が必要です。

---

## トラブルシューティング

| 症状 | 原因 | 対処 |
|------|------|------|
| `port already in use` | 8000番が使用中 | `docker compose down` して再起動 |
| `no such file: .env` | .env がない | `.env.example` をコピーして作成 |
| `pip install` が遅い | 初回ビルド | 2回目以降はキャッシュが効く |
| コードを変えたのに反映されない | 古いイメージが残っている | `--build` フラグを付けて再起動 |

---

## 他プロジェクトへの転用

`docker-new-project-prompt.md` にプロジェクト情報を埋めて AI に渡すと、そのプロジェクト用の Dockerfile 一式を生成できます。
