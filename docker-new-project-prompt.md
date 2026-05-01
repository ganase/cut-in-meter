# 新規プロジェクト Docker 化プロンプト

このファイルを新しいプロジェクトにコピーし、`【】` 内を埋めてから AI（Claude等）に渡してください。
`Dockerfile`・`docker-compose.yml`・`.dockerignore`・エンジニアガイドの更新を一括で依頼できます。

---

## AI への依頼プロンプト（ここをコピーして使う）

```
以下のプロジェクト情報をもとに、プロダクションレベルで使えるDocker構成一式を作成してください。

## 作成してほしいもの
1. Dockerfile
2. docker-compose.yml
3. .dockerignore
4. docker-engineer-guide.md（このプロジェクト固有の内容に更新）

---

## プロジェクト情報

### 基本情報
- プロジェクト名: 【例: my-api】
- 一言説明: 【例: 社内向け予約管理API】

### 言語・ランタイム
- 言語: 【例: Python / Node.js / Go / Ruby / Java】
- バージョン: 【例: Python 3.12 / Node 20 / Go 1.22】
- フレームワーク: 【例: FastAPI / Express / Gin / Rails】

### 起動方法
- 起動コマンド: 【例: uvicorn app.main:app --host 0.0.0.0 --port 8000】
- 公開ポート: 【例: 8000】
- アプリの種類: 【Webサーバー / バッチ / ワーカー / CLI ツール】

### 依存関係
- 依存ファイル: 【例: requirements.txt / package.json / go.mod / Gemfile】
- ビルドステップがあれば: 【例: npm run build / なし】
- システムパッケージが必要なら: 【例: libgl1（画像処理）/ ffmpeg / なし】

### 環境変数
（必要な環境変数を列挙してください）
- 【例: DATABASE_URL — 必須 — DBの接続文字列】
- 【例: API_KEY — 必須 — 外部サービスのキー】
- 【例: DEBUG — 任意 — デフォルト false】

### データ永続化
- 永続化が必要なディレクトリ: 【例: data/ / uploads/ / なし】
- 理由: 【例: ユーザーがアップロードした画像を保存】

### その他の考慮事項
- 複数サービスが必要か: 【例: アプリ + PostgreSQL + Redis / アプリのみ】
- 特別な要件: 【例: カメラデバイスへのアクセスが必要 / GPUが必要 / なし】

---

## 品質要件

以下を満たしてください：
- requirements.txt（または依存ファイル）を先にコピーしてキャッシュを最大化
- 軽量なベースイメージを使う（slim / alpine 等）
- .dockerignore で不要ファイルを除外（.venv, node_modules, .env, .git 等）
- docker-compose.yml では env_file で .env を読み込む
- データ永続化が必要な場合は volumes を設定する
- restart: unless-stopped を設定する
- セキュリティ上 root 以外のユーザーで実行する（可能であれば）

## 参考にしてほしいガイドのスタイル
（このプロジェクトの docker-engineer-guide.md のスタイルに合わせてください）
- 構造の説明にはコードブロック内コメントを使う
- 主要コマンドを一覧で示す
- 環境変数はテーブル形式
- トラブルシューティングはテーブル形式
```

---

## 使い方メモ

1. 上のプロンプトをコピー
2. `【】` の部分を実際のプロジェクト情報で埋める
3. Claude（またはほかのAI）に貼り付けて送信
4. 生成されたファイルをプロジェクトルートに配置
5. `docker compose up` で動作確認

## チェックリスト（AI生成後の確認）

- [ ] `docker build .` がエラーなく完了する
- [ ] `docker compose up` でアプリが起動する
- [ ] ブラウザ（またはcurl）でレスポンスが返る
- [ ] コンテナ停止後もデータが `data/` フォルダに残っている
- [ ] `.env` が誤ってイメージに含まれていないか確認（`docker inspect` で確認）
