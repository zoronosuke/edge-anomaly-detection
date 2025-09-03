# Edge Anomaly Detection System

研究用エッジ異常検知システム（CSV/JSON データベース版）

## 🎯 概要

このシステムは、エッジデバイス（Jetson Nano等）が撮影した映像をリアルタイムでサーバに送信し、サーバ側で機械学習モデル（YOLOv8）により人の検出を行い、異常があればLINE通知するシステムです。

研究用途として、データベースの代わりにCSV/JSONファイルでデータを管理します。

## 📁 プロジェクト構成

```
edge-anomaly-detection/
├── server/                 # サーバー側コード
│   ├── main.py            # FastAPI メインアプリケーション
│   ├── models.py          # データモデル定義
│   ├── data_manager.py    # CSV/JSON データ管理
│   └── line_notifier.py   # LINE通知システム
├── client/                 # クライアント側コード
│   ├── edge_client.py     # 実際のエッジデバイス用
│   ├── dummy_client.py    # テスト用ダミークライアント
│   └── config.json        # クライアント設定例
├── tools/                  # 管理ツール
│   └── management.py      # データ分析・管理ツール
├── data/                   # データ保存ディレクトリ
│   ├── events.csv         # イベントデータ
│   ├── system_logs.json   # システムログ
│   └── images/            # 検出時の画像
├── requirements.txt        # Python依存関係
├── .env.example           # 環境変数テンプレート
├── start_server.bat       # サーバー起動スクリプト
└── start_dummy_client.bat # ダミークライアント起動スクリプト
```

## 🚀 セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env.example` を `.env` にコピーして設定を編集：

```bash
copy .env.example .env
```

重要な設定項目：
- `API_KEY`: API認証キー
- `LINE_CHANNEL_ACCESS_TOKEN`: LINE Bot のアクセストークン
- `LINE_CHANNEL_SECRET`: LINE Bot のチャンネルシークレット
- `LINE_USER_ID`: 通知先のLINEユーザーID

### 3. ディレクトリの作成

```bash
mkdir data
mkdir data\images
```

## 🖥️ 使用方法

### サーバーの起動

#### 方法1: バッチファイルを使用（Windows）
```bash
start_server.bat
```

#### 方法2: 直接起動
```bash
cd server
python main.py
```

サーバーは `http://localhost:8000` で起動します。

### クライアントの実行

#### ダミークライアント（テスト用）
```bash
start_dummy_client.bat
```

または：
```bash
cd client
python dummy_client.py --device-id test-device --duration 60
```

#### 実際のエッジデバイス
```bash
cd client
python edge_client.py --device-id jetson-001 --camera 0
```

## 📊 データ形式

### イベントデータ (events.csv)
```csv
event_id,device_id,timestamp,person_count,anomaly_flag,image_filename,confidence_threshold,processing_time_ms
uuid1,jetson-001,2025-09-04 10:30:15.123456,2,True,uuid1.jpg,0.5,150
```

### システムログ (system_logs.json)
```json
[
  {
    "log_id": "uuid",
    "timestamp": "2025-09-04T10:30:15.123456",
    "level": "INFO",
    "device_id": "jetson-001",
    "message": "検出処理完了",
    "details": {"person_count": 2}
  }
]
```

## 🔧 管理ツール

### データ分析
```bash
cd tools
python management.py analyze --data-dir ../data
```

### ログ分析
```bash
python management.py logs --data-dir ../data
```

### 古いデータのクリーンアップ
```bash
python management.py cleanup --data-dir ../data --days 30
```

## 🌐 API エンドポイント

### メインエンドポイント

- `POST /ingest` - 画像データの受信・処理
- `GET /` - ヘルスチェック
- `GET /status/{device_id}` - デバイス状態取得
- `GET /events` - イベント一覧取得
- `GET /logs` - システムログ取得

### 使用例

```bash
# ヘルスチェック
curl http://localhost:8000/

# イベント一覧取得
curl "http://localhost:8000/events?limit=10&anomaly_only=true"

# デバイス状態取得
curl http://localhost:8000/status/jetson-001
```

## 🔔 LINE通知設定

1. LINE Developers でBot作成
2. チャンネルアクセストークンとシークレットを取得
3. Bot をグループまたは個人チャットに追加
4. ユーザーIDまたはグループIDを取得
5. `.env` ファイルに設定

通知メッセージ例：
```
🚨 [人検出アラート]
デバイス: jetson-001
検出数: 2人
時刻: 2025-09-04 10:30:15
イベントID: uuid
```

## ⚙️ 設定項目

### サーバー設定
- `SERVER_HOST`: サーバーホスト（デフォルト: 0.0.0.0）
- `SERVER_PORT`: サーバーポート（デフォルト: 8000）
- `CONFIDENCE_THRESHOLD`: YOLO検出閾値（デフォルト: 0.5）
- `ALERT_COOLDOWN_SECONDS`: 通知クールダウン時間（デフォルト: 300秒）

### クライアント設定
- `--fps`: 送信フレームレート（デフォルト: 1.0）
- `--width`: 画像幅（デフォルト: 640）
- `--height`: 画像高さ（デフォルト: 360）
- `--quality`: JPEG品質（デフォルト: 80）

## 🧪 研究・実験用機能

### 複数デバイス対応
```bash
# デバイス1
python dummy_client.py --device-id jetson-001 --fps 1.0

# デバイス2
python dummy_client.py --device-id jetson-002 --fps 2.0

# デバイス3
python dummy_client.py --device-id jetson-003 --fps 0.5
```

### パフォーマンステスト
```bash
# 高フレームレートテスト
python dummy_client.py --fps 5.0 --duration 120

# 低品質画像テスト
python dummy_client.py --quality 50 --width 320 --height 240
```

### データ分析
```bash
# 統計表示
python tools/management.py analyze

# エラーログ確認
python tools/management.py logs
```

## 🚨 トラブルシューティング

### よくある問題

1. **YOLOモデルのダウンロードに時間がかかる**
   - 初回起動時は `yolov8n.pt` のダウンロードが発生します
   - ネットワーク環境により数分かかる場合があります

2. **LINE通知が送信されない**
   - `.env` ファイルの設定を確認
   - Bot がチャットに追加されているか確認
   - ユーザーID/グループIDが正しいか確認

3. **カメラが認識されない**
   - カメラデバイスIDを確認（通常は0、複数ある場合は1, 2...）
   - カメラが他のアプリケーションで使用されていないか確認

4. **メモリ不足エラー**
   - 画像サイズを小さくする（320x240など）
   - JPEG品質を下げる（50-70）
   - 送信フレームレートを下げる

### ログ確認
```bash
# システムログ確認
python tools/management.py logs

# サーバーコンソール出力を確認
# エラーメッセージが表示される
```

## 📈 今後の拡張予定

- [ ] Webダッシュボード追加
- [ ] より詳細な統計機能
- [ ] 複数種類の物体検出対応
- [ ] リアルタイム監視画面
- [ ] データエクスポート機能

## 📝 ライセンス

このプロジェクトは研究用途で開発されています。
