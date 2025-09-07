#!/bin/bash
# Jetson Nano用サーバー起動スクリプト

set -e

echo "=========================================="
echo "Jetson Nano Edge Anomaly Detection Server"
echo "=========================================="

# 環境チェック
if [ -f /etc/nv_tegra_release ]; then
    echo "Jetson Info: $(cat /etc/nv_tegra_release)"
else
    echo "警告: Jetson Nanoが検出されません"
fi

# 実行方法の選択
echo ""
echo "起動方法を選択してください:"
echo "1) Docker環境で起動 (推奨)"
echo "2) Python 3.8仮想環境で起動"
echo "3) 現在の環境で起動"
echo ""

read -p "選択してください [1-3]: " choice

case $choice in
    1)
        echo "Docker環境で起動します..."
        
        # 設定ファイルの確認
        if [ ! -f .env ]; then
            echo "設定ファイルを作成します..."
            cp .env.example .env 2>/dev/null || echo "# 基本設定" > .env
        fi
        
        # Dockerビルドと起動
        echo "Dockerイメージをビルドしています..."
        sudo docker-compose -f docker-compose.jetson.yml --profile jetson build
        
        echo "サーバーを起動しています..."
        sudo docker-compose -f docker-compose.jetson.yml --profile jetson up -d
        
        echo ""
        echo "✓ サーバーが起動しました"
        echo "  URL: http://localhost:8000"
        echo "  ログ確認: sudo docker-compose -f docker-compose.jetson.yml logs -f"
        echo "  停止: sudo docker-compose -f docker-compose.jetson.yml down"
        ;;
        
    2)
        echo "Python 3.8仮想環境で起動します..."
        
        VENV_PATH="$HOME/venv-jetson-py38"
        if [ ! -d "$VENV_PATH" ]; then
            echo "エラー: 仮想環境が見つかりません"
            echo "先に setup_jetson.sh を実行してください"
            exit 1
        fi
        
        # 仮想環境をアクティベート
        source $VENV_PATH/bin/activate
        
        # 設定ファイルの確認
        if [ ! -f .env ]; then
            echo "設定ファイルを作成します..."
            cp .env.example .env 2>/dev/null || cat > .env << 'EOF'
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
API_KEY=jetson_api_key_here
PERSON_DETECTION_THRESHOLD=0.5
COOLDOWN_SECONDS=30
MAX_DETECTION_HISTORY=1000
DATA_DIR=./data
LOG_DIR=./logs
EOF
        fi
        
        # 必要なディレクトリの作成
        mkdir -p data logs
        
        # サーバー起動
        echo "サーバーを起動しています..."
        cd server
        python main.py
        ;;
        
    3)
        echo "現在の環境で起動します..."
        echo "警告: 互換性問題が発生する可能性があります"
        
        # 設定ファイルの確認
        if [ ! -f .env ]; then
            echo "設定ファイルを作成します..."
            cp .env.example .env 2>/dev/null || echo "# 設定が必要です" > .env
        fi
        
        # 必要なディレクトリの作成
        mkdir -p data logs
        
        # サーバー起動
        echo "サーバーを起動しています..."
        cd server
        python3 main.py
        ;;
        
    *)
        echo "無効な選択です"
        exit 1
        ;;
esac
