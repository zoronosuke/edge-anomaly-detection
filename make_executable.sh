# Jetson Nano用実行権限設定
# Linux/Unix環境でスクリプトに実行権限を与える

echo "Jetson Nano用スクリプトに実行権限を設定しています..."

chmod +x check_jetson_env.py
chmod +x setup_jetson.sh  
chmod +x start_jetson_server.sh

echo "実行権限の設定が完了しました。"
echo ""
echo "利用可能なスクリプト:"
echo "  ./check_jetson_env.py     - 環境互換性チェック"
echo "  ./setup_jetson.sh         - 環境セットアップ"
echo "  ./start_jetson_server.sh  - サーバー起動"
