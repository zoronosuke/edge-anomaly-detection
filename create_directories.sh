#!/bin/bash
# プロジェクトに必要なディレクトリ構造を作成

echo "=========================================="
echo "プロジェクトディレクトリ構造を作成中..."
echo "=========================================="

# 必要なディレクトリを作成
echo "📁 ディレクトリを作成中..."
mkdir -p logs
mkdir -p data
mkdir -p uploads
mkdir -p results
mkdir -p models
mkdir -p temp

# .gitkeepファイルを作成（空ディレクトリをGitで管理するため）
echo "📝 .gitkeepファイルを作成中..."
touch logs/.gitkeep
touch data/.gitkeep
touch uploads/.gitkeep
touch results/.gitkeep
touch models/.gitkeep
touch temp/.gitkeep

# YOLOv8モデルファイルの確認
if [ ! -f "yolov8n.pt" ] && [ ! -f "models/yolov8n.pt" ]; then
    echo "⚠️  YOLOv8nモデルファイルが見つかりません"
    echo "    初回実行時に自動ダウンロードされます"
fi

echo ""
echo "✅ ディレクトリ構造の作成が完了しました："
echo "  📁 logs/      - ログファイル"
echo "  📁 data/      - データファイル (events.csv, performance_metrics.csv)"
echo "  📁 uploads/   - アップロードされた画像"
echo "  📁 results/   - 処理結果"
echo "  📁 models/    - AIモデルファイル"
echo "  📁 temp/      - 一時ファイル"

echo ""
echo "🚀 準備完了！サーバーを起動できます:"
echo "   python server/main.py"

# ディレクトリの権限確認
echo ""
echo "📋 作成されたディレクトリ一覧:"
ls -la | grep "^d" | grep -E "(logs|data|uploads|results|models|temp)"
