アプリを開発してください．ただ，データベースは今は使わなくていいです．csvファイルか，jsonファイルにいい感じに記録してほしいです．
.gitignore に venv/を入れるなど，gitに上げるときにおかしくならないようにして．

# 🚀 Edge Anomaly Detection System

エッジデバイスからの映像をリアルタイムでサーバに送信し、機械学習による人検出と異常通知を行うシステムです。

**🎯 Jetson Nano対応**: JetPack 4.6.6環境での動作を最適化済み

## 🛠️ システム構成

```
[エッジデバイス]          [サーバ]
  └─ カメラ               ├─ FastAPI (画像受信)
  └─ 画像送信             ├─ YOLOv8n (人検出)
                         ├─ LINE通知
                         └─ CSV/JSON保存
```

## 🔧 対応プラットフォーム

- **x86_64**: Windows, Linux, macOS
- **ARM64**: Jetson Nano (JetPack 4.6.6)
- **Python**: 3.8+ (Jetson Nano: 3.8推奨)

## 📁 プロジェクト構造

```
edge-anomaly-detection/
├── server/                      # サーバサイドコード
│   ├── main.py                 # FastAPI メインアプリ
│   └── line_notifier.py        # LINE通知モジュール
├── edge/                       # エッジデバイスコード
│   └── client.py               # カメラクライアント
├── tools/                      # 分析ツール
│   └── performance_analyzer.py
├── data/                       # データ保存ディレクトリ
├── logs/                       # ログファイル
├── requirements.txt            # Python依存関係（汎用）
├── requirements-jetson.txt     # Jetson Nano専用依存関係
├── .env.example               # 環境変数テンプレート
├── config.json                # 設定ファイル
├── check_jetson_env.py        # Jetson環境チェック
├── setup_jetson.sh            # Jetson環境セットアップ
├── start_jetson_server.sh     # Jetson用起動スクリプト
├── Dockerfile.jetson          # Jetson用Dockerファイル
├── docker-compose.jetson.yml  # Jetson用Docker Compose
├── start_server.bat           # サーバ起動スクリプト（Windows）
├── start_client.bat           # クライアント起動スクリプト（Windows）
└── test_system.py             # システムテストスクリプト
```

## 🚀 クイックスタート

### 📥 リポジトリのクローンと基本セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/zoronosuke/edge-anomaly-detection.git
cd edge-anomaly-detection

# 実行権限の設定（Linux/Jetsonの場合）
bash make_executable.sh
```

### 🏠 標準環境（Windows x86_64）

#### 1. 環境セットアップ
```bash
# 方法A: 自動セットアップ（推奨）
tasks.bat setup-dev

# 方法B: 手動セットアップ
python -m venv venv
venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2. 設定ファイルの準備
```bash
# 環境変数ファイルをコピー
copy .env.example .env

# .envファイルを編集（任意のテキストエディタで）
# API_KEY=your_secret_api_key
# LINE_CHANNEL_ACCESS_TOKEN=your_line_token（オプション）
```

#### 3. サーバー起動
```bash
# 🚀 簡単起動（推奨）
start_server.bat

# 🚀 または手動起動
venv\Scripts\activate.bat
python server\main.py
```

#### 4. クライアント起動（別ターミナル）
```bash
# 🚀 簡単起動
start_client.bat --device-id windows-pc-001

# 🚀 または手動起動
venv\Scripts\activate.bat
python edge\client.py --device-id windows-pc-001 --server-url http://localhost:8000
```

### 🤖 Jetson Nano環境

#### 1. 環境確認
```bash
# Python環境とJetPackの互換性をチェック
python3 check_jetson_env.py
```

#### 2. 環境セットアップ（推奨順）

**Option A: 自動セットアップ（最推奨）**
```bash
# インタラクティブセットアップ
./setup_jetson.sh

# 推奨選択肢:
# 1) Docker環境での実行（最推奨）
# 2) Python 3.8仮想環境のセットアップ
# 3) 現在のPython環境での強制実行（非推奨）
```

**Option B: Docker環境（手動）**
```bash
# NVIDIA Docker runtimeが必要
sudo docker run --runtime nvidia -it --rm \
  --network host --ipc=host \
  --name jetson-edge-detection \
  -v $(pwd):/workspace \
  -w /workspace \
  -p 8000:8000 \
  nvcr.io/nvidia/l4t-ml:r32.7.1-py3
```

**Option C: Python 3.8仮想環境（手動）**
```bash
# Python 3.8のインストール
sudo apt update
sudo apt install -y python3.8 python3.8-venv python3.8-dev

# 仮想環境の作成とアクティベート
python3.8 -m venv ~/venv-jetson-py38
source ~/venv-jetson-py38/bin/activate

# 依存関係のインストール
pip install --upgrade pip
pip install -r requirements-jetson.txt
```

#### 3. 環境のアクティベート（次回起動時）
```bash
# セットアップ完了後は以下のコマンドで環境をアクティベート
source activate_jetson_env.sh
```

#### 4. サーバー起動
```bash
# 🚀 簡単起動スクリプト（推奨）
./start_jetson_server.sh

# 🚀 または手動起動
python server/main.py
```

#### 5. セットアップの確認
```bash
# 環境が正しく構築されているかテスト
./test_jetson_setup.sh
```

### 🧪 動作確認

#### システムテスト
```bash
# 基本テスト（Windows）
python basic_test.py

# 完全なシステムテスト
python test_system.py

# Windows用バッチファイル
tasks.bat test
```

#### 手動テスト
```bash
# サーバー接続確認
curl http://localhost:8000/

# 画像アップロードテスト（cURLがある場合）
curl -X POST "http://localhost:8000/ingest" \
  -H "Authorization: Bearer your_api_key" \
  -F "file=@test_image.jpg" \
  -F "device_id=test-device"
```

### 🔧 トラブルシューティング

#### Jetson Nano環境の問題
```bash
# 環境の再確認
python3 check_jetson_env.py

# セットアップの再実行
./setup_jetson.sh

# Docker環境にフォールバック
sudo docker run --runtime nvidia -it --rm \
  --network host \
  -v $(pwd):/workspace \
  nvcr.io/nvidia/l4t-ml:r32.7.1-py3
```

#### Windows環境の問題
```bash
# 仮想環境の再作成
rmdir /s venv
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### 📂 プロジェクト構造の確認
正常にセットアップできた場合、以下の構造が確認できます：
tasks.bat client jetson-001

# 🚀 またはバッチファイル使用
start_client.bat --device-id jetson-001

# 🚀 または手動起動
venv\Scripts\activate.bat
python edge\client.py --device-id jetson-001 --server-url http://localhost:8000 --api-key your_api_key
```

### 5. システムテスト

```bash
# 🧪 全テスト実行
tasks.bat test

# 🧪 基本テストのみ
tasks.bat test-basic

# 🧪 または個別実行
python basic_test.py
python test_system.py
```

## � データ保存形式

### events.csv
検出イベントの記録
```csv
event_id,device_id,timestamp,person_count,anomaly_flag,confidence_scores,processing_time_ms,image_filename
uuid123,jetson-001,2025-09-04T10:30:00,2,true,"[0.85, 0.92]",45.2,jetson-001_20250904_103000_abc123.jpg
```

### performance_metrics.csv
パフォーマンスメトリクス
```csv
timestamp,device_id,request_size_bytes,processing_time_ms,inference_time_ms,total_response_time_ms
2025-09-04T10:30:00,jetson-001,65432,45.2,23.1,78.5
```

## 🔧 API エンドポイント

### POST /ingest
画像をアップロードして人検出を実行

**リクエスト:**
- Header: `Authorization: Bearer your_api_key`
- Form data:
  - `file`: 画像ファイル (JPEG)
  - `device_id`: デバイスID
  - `ts`: タイムスタンプ (オプション)

**レスポンス:**
```json
{
  "event_id": "uuid123",
  "device_id": "jetson-001",
  "timestamp": "2025-09-04T10:30:00",
  "person_count": 2,
  "anomaly_detected": true,
  "confidence_scores": [0.85, 0.92],
  "processing_time_ms": 45.2
}
```

### GET /events
イベント履歴を取得

**パラメータ:**
- `device_id`: デバイスIDでフィルタ (オプション)
- `limit`: 取得件数 (デフォルト: 100)

### GET /metrics
パフォーマンスメトリクスを取得

## 📈 分析ツール

### パフォーマンス分析
```bash
cd tools
python performance_analyzer.py --data-dir ../data --output-report report.json --charts-dir ../charts
```

**生成される分析項目:**
- 検出性能統計
- 通信性能統計
- デバイス別比較
- 時系列グラフ
- レスポンス時間分布

## 📱 LINE通知設定

1. LINE Developersでチャンネル作成
2. `.env`ファイルに設定
```
LINE_CHANNEL_ACCESS_TOKEN=your_token
LINE_CHANNEL_SECRET=your_secret
```
3. `line_notifier.py`でuser_idを設定

## 🔧 設定オプション

### config.json
```json
{
  "detection": {
    "confidence_threshold": 0.5,
    "cooldown_seconds": 30
  },
  "data_storage": {
    "save_images": true,
    "image_quality": 85
  }
}
```

### 環境変数 (.env)
```
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
API_KEY=your_api_key_here
PERSON_DETECTION_THRESHOLD=0.5
COOLDOWN_SECONDS=30
DATA_DIR=./data
LOG_DIR=./logs
```

## 🧪 テスト

### システム全体テスト
```bash
python test_system.py
```

### 単体テスト
```bash
# サーバ接続テスト
curl http://localhost:8000/

# 画像アップロードテスト（cURL使用）
curl -X POST "http://localhost:8000/ingest" \
  -H "Authorization: Bearer your_api_key" \
  -F "file=@test_image.jpg" \
  -F "device_id=test-device"
```

## 📦 システム要件

- Python 3.8+
- OpenCV
- FastAPI
- PyTorch
- YOLOv8
- カメラデバイス（エッジ側）

## 🚀 デプロイ

### サーバデプロイ
```bash
# Docker使用例
docker build -t edge-anomaly-server .
docker run -p 8000:8000 -v ./data:/app/data edge-anomaly-server
```

### エッジデバイス（Jetson Nano）
```bash
# JetPack環境での追加設定
sudo apt-get install python3-opencv
pip install -r requirements.txt
```

## 📊 研究用データ収集

このシステムは研究目的で以下のデータを収集します：

1. **通信性能データ**
   - レイテンシ
   - スループット
   - パケットロス率

2. **検出性能データ**
   - 検出精度
   - 処理時間
   - 誤検知率

3. **システム性能データ**
   - 同時接続数
   - リソース使用量
   - 可用性

## 🤝 コントリビューション

1. Forkして作業ブランチを作成
2. 変更を実装
3. テストを実行
4. Pull Requestを作成

## 📄 ライセンス

このプロジェクトはMITライセンスです。

## 🙋‍♂️ サポート

問題や質問がある場合は、GitHubのIssuesを利用してください。

## 1．研究の目的

本研究では，**エッジデバイスが撮影した映像をリアルタイムでサーバに送信し，サーバ側で機械学習モデルにより「人の検出」を行い，異常があれば通知するシステム**を構築する．
具体的な目的は以下の通りである．

* **比較実験**

  * ローカル5Gとキャリア5Gにおける通信性能の比較
  * VPN利用の有無による遅延や安定性の評価
* **システム実証**

  * 複数のエッジデバイスから同時に送られるデータをサーバで処理可能にする
  * サーバ推論方式での帯域・遅延・通知精度を確認
* **応用可能性検証**

  * エッジAI＋通信基盤（ローカル5G/キャリア5G）の組み合わせが，監視・防犯・現場管理等のリアルタイム異常検知に有効かを明らかにする

---

## 2．システム全体構成（複数エッジデバイス対応）

### 2.1 アーキテクチャ概要

```
[複数Edge/Jetson Nano]
  ├─ カメラで1秒ごとに1フレーム取得
  ├─ JPEG圧縮（640×360, Q=80）
  ├─ HTTP POSTでサーバに送信
  └─ device_idで識別

           ⇣ ネットワーク（ローカル5G / キャリア5G / VPN）

[Server]
  ├ ingest API (FastAPI)
  │   └ 画像受信（device_id, ts 付き）
  ├ 推論モジュール (YOLOv8n / PyTorch)
  │   └ personクラスを検出（conf ≥ 0.5）
  ├ 通知モジュール
  │   └ LINE Messaging APIで警告通知
  ├ イベント管理
  │   └ 重複抑制・クールダウン（端末ごとに管理）
  └ 保存モジュール
      ├ DB（PostgreSQL）: 検知メタデータ保存
      └ S3互換ストレージ: 検出サムネイル保存
```

---

### 2.2 複数端末対応の工夫

* **device\_id必須**：各エッジデバイスから送信する際にユニークID（例：`jetson-001`）を付与
* **サーバ側辞書管理**：

  * `_last_alert_at[device_id]`
  * `_last_event_sig[device_id]`
    により，端末ごとにクールダウンと重複抑制を独立管理
* **データベース構造**：

  * `events (event_id, device_id, ts, person_count, anomaly_flag, image_url)`
    として，複数端末からのイベントを統一的に記録

---

## 3．データフロー

1. **エッジ処理**

   * カメラでフレーム取得（1fps）
   * JPEG圧縮（640×360, Q=80）
   * HTTP POST：`/ingest`

     * Body: 画像ファイル
     * Form: `device_id`, `ts`
     * Header: `X-Api-Key`

2. **サーバ処理**

   * FastAPIで受信
   * YOLOモデルで推論 → personクラスの有無を判定
   * イベント管理：端末ごとのクールダウン／重複抑制
   * LINE通知：異常時にBotアカウントから通知（Flex Message対応可）
   * DB保存：検知結果＋メタデータ
   * 画像保存：S3互換ストレージへ（後で参照可能）

3. **通知処理**

   * LINEメッセージ例：

     ```
     [人検出] device=jetson-001 count=2
     時刻: 2025-09-03 12:34:56
     ```
   * 将来はサムネイル画像のURLも添付

---

## 4．実験項目（研究として）

### 4.1 通信性能比較

* **条件**：

  * VPNなしローカル5G
  * VPNありローカル5G
  * VPNありキャリア5G
* **指標**：

  * レイテンシ（ping, HTTP応答時間）
  * スループット（iperf3）
  * ジッター／パケットロス率
  * 接続確立時間

### 4.2 システム性能検証

* 複数端末同時送信（例：3台, 5台, 10台）でサーバが処理可能か
* 1fps, 2fps, 5fps と送信周期を変化させた場合の帯域・CPU負荷・通知遅延
* 誤検知／未検知率の確認（モデル閾値調整）

### 4.3 応用実証

* 夜間や遠距離での検出性能
* ネットワーク障害時の再送挙動
* 通知の実運用有効性（スパム防止・クールダウン機能の効果）

---

## 5．使用技術

* **言語**：Python
* **エッジ**：Jetson Nano（OpenCV + Requests）
* **サーバ**：FastAPI + Uvicorn
* **モデル**：YOLOv8n (ultralytics)
* **通知**：LINE Messaging API
* **DB**：PostgreSQL（イベントログ管理）
* **ストレージ**：MinIO（S3互換）

---

## 6．研究の意義

* ローカル5Gとキャリア5Gの通信性能を，\*\*実際のエッジAIアプリケーション（人検出）\*\*の観点から比較できる．
* 複数エッジデバイスの同時接続を扱う設計により，**将来の大規模システム（監視・スマート工場等）に直結**する．
* 「サーバ推論方式」の限界（帯域・遅延）を明らかにでき，将来的に「ハイブリッド推論」へ移行する際の基礎データになる．

---

👉 このドキュメントをベースに，次は **システム図（ネットワーク構成図／データフロー図）を図解**するとより発表資料向きになります．

ご希望ですか？それともまずは **この文章をLaTeXレポート形式**にまとめ直しましょうか？
