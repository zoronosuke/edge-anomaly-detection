# 🚀 Edge Anomaly Detection System - クローンから実行まで

このガイドでは、プロジェクトをクローンしてから実行するまでの詳細な手順を説明します。

## 📋 目次

- [前提条件](#前提条件)
- [Windows環境での実行](#windows環境での実行)
- [Jetson Nano環境での実行](#jetson-nano環境での実行)
- [Docker環境での実行](#docker環境での実行)
- [トラブルシューティング](#トラブルシューティング)

## 前提条件

### 共通
- Git が インストールされていること
- Python 3.8以上（推奨）
- インターネット接続（依存関係のダウンロード用）

### Jetson Nano固有
- JetPack 4.6.6がインストール済み
- NVIDIA Container Runtime（Docker使用時）

## Windows環境での実行

### ステップ 1: リポジトリのクローン

```bash
# コマンドプロンプトまたはPowerShellを開く
git clone https://github.com/zoronosuke/edge-anomaly-detection.git
cd edge-anomaly-detection
```

### ステップ 2: 環境のセットアップ

#### 方法A: 自動セットアップ（推奨）
```bash
# 開発環境の自動セットアップ
tasks.bat setup-dev
```

#### 方法B: 手動セットアップ
```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
venv\Scripts\activate.bat

# 依存関係のインストール
pip install --upgrade pip
pip install -r requirements.txt
```

### ステップ 3: 設定ファイルの準備

```bash
# 環境変数ファイルのコピー
copy .env.example .env

# .envファイルを編集（メモ帳やVS Codeなどで）
notepad .env
```

**.env ファイルの設定例:**
```env
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
API_KEY=your_secret_api_key_here
PERSON_DETECTION_THRESHOLD=0.5
COOLDOWN_SECONDS=30
DATA_DIR=./data
LOG_DIR=./logs
# LINE通知（オプション）
LINE_CHANNEL_ACCESS_TOKEN=your_line_token_here
```

### ステップ 4: サーバーの起動

#### 方法A: バッチファイルを使用（推奨）
```bash
# サーバーを起動
start_server.bat
```

#### 方法B: 手動起動
```bash
# 仮想環境を有効化（まだの場合）
venv\Scripts\activate.bat

# サーバーを起動
python server\main.py
```

### ステップ 5: クライアントの起動（別のコマンドプロンプト）

#### 方法A: バッチファイルを使用（推奨）
```bash
# 新しいコマンドプロンプトを開いて
cd edge-anomaly-detection
start_client.bat --device-id windows-pc-001
```

#### 方法B: 手動起動
```bash
# 仮想環境を有効化
venv\Scripts\activate.bat

# クライアントを起動
python edge\client.py --device-id windows-pc-001 --server-url http://localhost:8000
```

### ステップ 6: 動作確認

1. ブラウザで `http://localhost:8000` にアクセス
2. カメラが起動し、映像が表示されることを確認
3. 人が検出されると、通知とデータ保存が行われることを確認

## Jetson Nano環境での実行

### ステップ 1: リポジトリのクローン

```bash
# ターミナルを開く
git clone https://github.com/zoronosuke/edge-anomaly-detection.git
cd edge-anomaly-detection

# 実行権限の設定
bash make_executable.sh
```

### ステップ 2: 環境の確認

```bash
# Python環境とJetPackの互換性をチェック
python3 check_jetson_env.py
```

このコマンドで、以下の項目がチェックされます：
- Python バージョン（3.8推奨）
- JetPack バージョン
- 必要なパッケージの存在
- CUDA サポート

### ステップ 3: 環境のセットアップ

#### 方法A: 自動セットアップ（推奨）
```bash
# インタラクティブセットアップを実行
./setup_jetson.sh
```

セットアップ画面で選択肢が表示されます：
1. **Docker環境での実行（最推奨）**: NVIDIA L4T MLコンテナを使用
2. **Python 3.8仮想環境のセットアップ**: ローカル環境に仮想環境を構築
3. **現在のPython環境での強制実行（非推奨）**: 互換性問題の可能性あり

**推奨**: 選択肢 1 または 2 を選択してください。

#### 方法B: Docker環境（手動セットアップ）
```bash
# NVIDIA Dockerランタイムが必要
sudo docker run --runtime nvidia -it --rm \
    --network host --ipc=host \
    --name jetson-edge-detection \
    -v $(pwd):/workspace \
    -w /workspace \
    -p 8000:8000 \
    nvcr.io/nvidia/l4t-ml:r32.7.1-py3 \
    bash
```

Docker内で：
```bash
pip install -r requirements-jetson.txt
python server/main.py
```

#### 方法C: Python 3.8仮想環境（手動セットアップ）
```bash
# Python 3.8のインストール
sudo apt update
sudo apt install -y python3.8 python3.8-venv python3.8-dev python3.8-distutils

# 仮想環境の作成
python3.8 -m venv ~/venv-jetson-py38

# 仮想環境の有効化
source ~/venv-jetson-py38/bin/activate

# 依存関係のインストール
pip install --upgrade pip
pip install -r requirements-jetson.txt
```

### ステップ 4: 設定ファイルの準備

```bash
# 環境変数ファイルのコピー
cp .env.example .env

# .envファイルを編集
nano .env
```

### ステップ 5: 環境のアクティベート（次回起動時）

セットアップ完了後は、以下のコマンドで簡単に環境をアクティベートできます：

```bash
# 作成されたアクティベーションスクリプトを使用
source activate_jetson_env.sh
```

### ステップ 6: サーバーの起動

#### 方法A: 起動スクリプトを使用（推奨）
```bash
./start_jetson_server.sh
```

#### 方法B: 手動起動
```bash
# 環境がアクティブの場合
python server/main.py
```

### ステップ 7: セットアップの確認

```bash
# 環境が正しく構築されているかテスト
./test_jetson_setup.sh
```

このテストで以下が確認されます：
- 仮想環境の存在
- 主要パッケージのインポート
- PyTorch、OpenCV、FastAPIなどの動作

## Docker環境での実行

### 標準Docker（x86_64）

```bash
# イメージのビルド
docker build -t edge-anomaly-server .

# コンテナの実行
docker run -p 8000:8000 -v ./data:/app/data edge-anomaly-server
```

### Docker Compose

```bash
# サービスの起動
docker-compose up -d

# ログの確認
docker-compose logs -f
```

### Jetson Nano用Docker Compose

```bash
# Jetson専用のCompose設定を使用
docker-compose -f docker-compose.jetson.yml up -d
```

## 動作確認とテスト

### 基本テスト

```bash
# 基本動作テスト
python basic_test.py

# システム全体テスト
python test_system.py
```

### Windows用テストコマンド

```bash
# 全テストの実行
tasks.bat test

# 基本テストのみ
tasks.bat test-basic
```

### 手動動作確認

1. **サーバー接続確認**
   ```bash
   curl http://localhost:8000/
   ```

2. **API テスト**（cURLがインストールされている場合）
   ```bash
   curl -X POST "http://localhost:8000/ingest" \
     -H "Authorization: Bearer your_api_key" \
     -F "file=@test_image.jpg" \
     -F "device_id=test-device"
   ```

3. **ブラウザでの確認**
   - http://localhost:8000 にアクセス
   - API ドキュメント: http://localhost:8000/docs

## トラブルシューティング

### Windows環境でよくある問題

#### Python が見つからない
```bash
# Python のパス確認
where python

# Python 3.x の確認
python --version
```

#### 仮想環境のアクティベートに失敗
```bash
# PowerShell の場合
venv\Scripts\Activate.ps1

# 実行ポリシーエラーの場合
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### パッケージインストールエラー
```bash
# pipのアップグレード
python -m pip install --upgrade pip

# キャッシュクリア
pip cache purge

# requirements を一つずつインストール
pip install fastapi uvicorn aiofiles requests
```

### Jetson Nano環境でよくある問題

#### Python 3.8が見つからない
```bash
# Python 3.8のインストール
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install -y python3.8 python3.8-venv python3.8-dev
```

#### PyTorchインストールエラー
```bash
# Jetson用PyTorchの手動インストール
wget https://nvidia.box.com/shared/static/fjtbno0vpo676a25cgvuqc1wty0fkkg6.whl -O torch-1.10.0-cp38-cp38-linux_aarch64.whl
pip install torch-1.10.0-cp38-cp38-linux_aarch64.whl
```

#### CUDA not available エラー
```bash
# CUDA環境の確認
nvcc --version
nvidia-smi

# 環境変数の設定
export CUDA_HOME=/usr/local/cuda
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH
```

### 共通の問題

#### ポート8000がすでに使用中
```bash
# 使用中のプロセスを確認
# Windows
netstat -ano | findstr :8000

# Linux/Jetson
lsof -i :8000
netstat -tuln | grep :8000

# 別のポートを使用
python server/main.py --port 8001
```

#### カメラデバイスが見つからない
```bash
# カメラデバイスの確認
# Windows
python -c "import cv2; print('Cameras:', [i for i in range(5) if cv2.VideoCapture(i).isOpened()])"

# Linux/Jetson
ls /dev/video*
v4l2-ctl --list-devices
```

#### メモリ不足エラー（Jetson Nano）
```bash
# スワップの設定
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永続化
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## サポートとヘルプ

問題が解決しない場合は：

1. **ログファイルを確認**: `logs/server.log`
2. **Issue を作成**: [GitHub Issues](https://github.com/zoronosuke/edge-anomaly-detection/issues)
3. **環境情報を提供**: `python check_jetson_env.py` の出力結果

## 次のステップ

正常に動作したら：

1. **設定のカスタマイズ**: `config.json` と `.env` ファイルの調整
2. **LINE通知の設定**: LINE Developers でのチャンネル作成
3. **複数デバイスの接続**: 追加のエッジデバイスの設定
4. **パフォーマンス分析**: `tools/performance_analyzer.py` の実行

---

**🎉 セットアップが完了したら、エッジAI異常検知システムをお楽しみください！**
