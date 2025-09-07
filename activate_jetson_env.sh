#!/bin/bash

echo "🤖 Jetson Nano環境をアクティベートしています..."

# 仮想環境の確認と選択
VENV_UPDATED="$HOME/venv-jetson-py38"
VENV_COMPAT="$HOME/venv-jetson-py38-compat"

if [ -d "$VENV_UPDATED" ]; then
    echo "✅ Python 3.8仮想環境(更新版)を検出"
    source "$VENV_UPDATED/bin/activate"
    VENV_TYPE="updated"
elif [ -d "$VENV_COMPAT" ]; then
    echo "✅ Python 3.8仮想環境(互換版)を検出"
    source "$VENV_COMPAT/bin/activate"
    VENV_TYPE="compatible"
else
    echo "⚠️  仮想環境が見つかりません。"
    echo "   ./setup_jetson.sh を実行してセットアップしてください。"
    exit 1
fi

# 依存関係の競合チェック
echo "📋 依存関係をチェックしています..."

numpy_version=$(python -c "import numpy; print(numpy.__version__)" 2>/dev/null || echo "not installed")
ultralytics_version=$(python -c "import ultralytics; print(ultralytics.__version__)" 2>/dev/null || echo "not installed")

echo "  numpy: $numpy_version"
echo "  ultralytics: $ultralytics_version"

# 競合チェック
if [[ "$numpy_version" == "1.19."* ]] && [[ "$ultralytics_version" == "8.0.2"* ]]; then
    echo "⚠️  依存関係の競合が検出されました。"
    echo "   ./setup_jetson.sh を実行して修正してください。"
elif [[ "$numpy_version" == "1.22."* ]] || [[ "$numpy_version" == "1.2"[3-9]* ]]; then
    echo "✅ 依存関係は正常です (更新版)。"
elif [[ "$numpy_version" == "1.19.5" ]] && [[ "$ultralytics_version" == "8.0.100" ]]; then
    echo "✅ 依存関係は正常です (互換版)。"
else
    echo "⚠️  パッケージバージョンを確認してください。"
fi

echo ""
echo "🚀 環境の準備が完了しました。"
echo "使用中の仮想環境: $VENV_TYPE"
echo ""
echo "利用可能なコマンド:"
echo "  python edge/client.py --help      - エッジクライアントのヘルプ"
echo "  python server/main.py             - サーバー起動"
echo "  python check_jetson_env.py        - 環境チェック"
