#!/bin/bash
# クイックスタートスクリプト - Edge Anomaly Detection System

set -e

echo "🚀 Edge Anomaly Detection System - Quick Start"
echo "=============================================="

# 現在のプラットフォームを検出
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [ -f /etc/nv_tegra_release ]; then
        PLATFORM="jetson"
        echo "📱 Platform: Jetson Nano detected"
    else
        PLATFORM="linux"
        echo "🐧 Platform: Linux detected"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
    echo "🍎 Platform: macOS detected"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    PLATFORM="windows"
    echo "🪟 Platform: Windows detected"
else
    PLATFORM="unknown"
    echo "❓ Platform: Unknown"
fi

echo ""

# 実行権限の設定（Linux/Jetson/macOS）
if [[ "$PLATFORM" != "windows" ]]; then
    echo "Setting execute permissions..."
    chmod +x setup_jetson.sh 2>/dev/null || true
    chmod +x start_jetson_server.sh 2>/dev/null || true  
    chmod +x test_jetson_setup.sh 2>/dev/null || true
    chmod +x check_jetson_env.py 2>/dev/null || true
fi

# プラットフォーム別セットアップ
case $PLATFORM in
    "jetson")
        echo "🤖 Jetson Nano環境のセットアップを開始します"
        echo ""
        echo "推奨セットアップ順序:"
        echo "1. 環境確認: python3 check_jetson_env.py"
        echo "2. セットアップ: ./setup_jetson.sh"
        echo "3. サーバー起動: ./start_jetson_server.sh"
        echo ""
        
        read -p "環境確認を実行しますか? [y/N]: " check_env
        if [[ $check_env == [yY] ]]; then
            echo "環境確認を実行中..."
            python3 check_jetson_env.py
        fi
        
        echo ""
        read -p "自動セットアップを実行しますか? [y/N]: " auto_setup
        if [[ $auto_setup == [yY] ]]; then
            ./setup_jetson.sh
        else
            echo "手動セットアップを選択した場合:"
            echo "  ./setup_jetson.sh を実行してください"
        fi
        ;;
        
    "linux")
        echo "🐧 Linux環境のセットアップ"
        
        # Python仮想環境の作成
        if [ ! -d "venv" ]; then
            echo "Python仮想環境を作成中..."
            python3 -m venv venv
        fi
        
        echo "仮想環境をアクティベート中..."
        source venv/bin/activate
        
        echo "依存関係をインストール中..."
        pip install --upgrade pip
        pip install -r requirements.txt
        
        echo "✅ セットアップ完了！"
        echo ""
        echo "次のステップ:"
        echo "1. 設定: cp .env.example .env && nano .env"  
        echo "2. サーバー起動: source venv/bin/activate && python server/main.py"
        ;;
        
    "macos")
        echo "🍎 macOS環境のセットアップ"
        
        # Homebrewの確認
        if ! command -v brew &> /dev/null; then
            echo "⚠️  Homebrewが見つかりません。OpenCVのインストールにHomebrewが推奨されます。"
            echo "Homebrew: https://brew.sh"
        fi
        
        # Python仮想環境の作成
        if [ ! -d "venv" ]; then
            echo "Python仮想環境を作成中..."
            python3 -m venv venv
        fi
        
        echo "仮想環境をアクティベート中..."
        source venv/bin/activate
        
        echo "依存関係をインストール中..."
        pip install --upgrade pip
        pip install -r requirements.txt
        
        echo "✅ セットアップ完了！"
        echo ""
        echo "次のステップ:"
        echo "1. 設定: cp .env.example .env && nano .env"
        echo "2. サーバー起動: source venv/bin/activate && python server/main.py"
        ;;
        
    "windows")
        echo "🪟 Windows環境では以下のコマンドを実行してください:"
        echo ""
        echo "# 自動セットアップ"
        echo "tasks.bat setup-dev"
        echo ""
        echo "# または手動セットアップ"
        echo "python -m venv venv"
        echo "venv\\Scripts\\activate.bat"
        echo "pip install -r requirements.txt"
        echo ""
        echo "# サーバー起動"
        echo "start_server.bat"
        ;;
        
    *)
        echo "❓ 不明なプラットフォームです。"
        echo "手動セットアップを試してください:"
        echo ""
        echo "python3 -m venv venv"
        echo "source venv/bin/activate"
        echo "pip install -r requirements.txt"
        echo "python server/main.py"
        ;;
esac

echo ""
echo "📚 詳細なセットアップ手順は SETUP_GUIDE.md をご覧ください"
echo "🐛 問題が発生した場合は以下を確認:"
echo "   - README.md のトラブルシューティングセクション"  
echo "   - logs/server.log ファイル"
echo "   - GitHub Issues: https://github.com/zoronosuke/edge-anomaly-detection/issues"
echo ""
echo "🎉 Happy coding!"
