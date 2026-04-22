# Cut-in-Meter

カメラ、画像、動画を読み込み、AI が「今この人に話しかけて大丈夫そうか」をジョーク判定するアプリです。

## まずこれだけ

### 0. GitHub から ZIP をダウンロード

1. GitHub の `Cut-in-Meter` リポジトリを開く
2. `Code` を押す
3. `Download ZIP` を選ぶ
4. ダウンロードした ZIP を解凍する
5. 解凍してできた `Cut-in-Meter` フォルダを開く

### Windows

1. ZIP を解凍したフォルダで `setup_windows.bat` を実行
2. Python 3.11 / 3.12 / 3.13 が無ければ、案内に従ってインストールして終了
3. セットアップ完了後、`.env` を開いて `OPENAI_API_KEY` を設定
4. `run_windows.bat` を実行
5. ブラウザで `http://127.0.0.1:8000` を開く

### macOS

1. ZIP を解凍したフォルダで `setup_macos.command` を実行
2. Python 3.11 / 3.12 / 3.13 が無ければ、案内に従ってインストールして終了
3. セットアップ完了後、`.env` を開いて `OPENAI_API_KEY` を設定
4. `run_macos.command` を実行
5. ブラウザで `http://127.0.0.1:8000` を開く

## ZIP ダウンロードから起動まで

### Windows

1. GitHub から `Download ZIP`
2. ZIP を解凍
3. 解凍したフォルダを開く
4. `setup_windows.bat` をダブルクリック
5. `.env` に `OPENAI_API_KEY` を設定
6. `run_windows.bat` をダブルクリック
7. `http://127.0.0.1:8000` を開く

### macOS

1. GitHub から `Download ZIP`
2. ZIP を解凍
3. 解凍したフォルダを開く
4. `setup_macos.command` を実行
5. `.env` に `OPENAI_API_KEY` を設定
6. `run_macos.command` を実行
7. `http://127.0.0.1:8000` を開く

## セットアップスクリプトの動作

- Python 3.11 / 3.12 / 3.13 が入っているか確認
- 入っていれば `.venv` を作成
- 依存関係をインストール
- `.env` が無ければ `.env.example` から作成
- 対応 Python が無ければユーザーにインストールを依頼して終了

## 手動セットアップ

### Windows

```bat
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
```

### macOS

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

`.env` に `OPENAI_API_KEY` を設定してください。

## 起動

### Windows

```bat
run_windows.bat
```

### macOS

```bash
./run_macos.command
```

## Features

- ブラウザのカメラ入力
- 画像ファイルの読み込み
- 動画ファイルの読み込みとフレーム指定
- OpenAI Responses API による LLM 画像判定
- 赤・黄・青の信号表示
- 8 秒ごとの実況モード
- 判定レベルの切り替え（慎重 / 標準 / ゆるめ）

## Environment Variables

- `OPENAI_API_KEY`: OpenAI API key
- `OPENAI_MODEL`: 既定は `gpt-5.4-mini`
- `OPENAI_TIMEOUT_SEC`: API タイムアウト秒数
- `FRAME_INTERVAL_SEC`: 実況モードの参考値
- `IMAGE_MAX_WIDTH`: クライアントで切り出す画像の最大辺
- `IMAGE_JPEG_QUALITY`: クライアントで送る JPEG 品質

## API

- `GET /api/health`: ヘルスチェック
- `POST /api/score`: 画像データ URL と判定レベルを受け取り、赤黄青の信号つきスコアを返す
- `POST /api/analyze/frame`: 既存互換の画像分析 API

## Notes

- 動画そのものを API に送るのではなく、現在フレームを切り出して画像として判定します。
- 判定は visible cues ベースの軽いジョーク用途です。重要な判断には使わないでください。
