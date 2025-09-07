# Jetson Nano用実行権限設定
# Linux/Unix環境でスクリプトに実行権限を与える

echo "Jetson Nano用スクリプトに実行権限を設定しています..."

chmod +x check_jetson_env.py
chmod +x setup_jetson.sh  
chmod +x start_jetson_server.sh
chmod +x test_jetson_setup.sh
chmod +x quick_start.sh
chmod +x create_directories.sh

# activate_jetson_env.shがある場合は権限を付与
if [ -f "activate_jetson_env.sh" ]; then
    chmod +x activate_jetson_env.sh
fi

echo "実行権限の設定が完了しました。"
echo "設定されたファイル:"
echo "  - check_jetson_env.py"
echo "  - setup_jetson.sh"
echo "  - start_jetson_server.sh"  
echo "  - test_jetson_setup.sh"
echo "  - quick_start.sh"
echo "  - create_directories.sh"
if [ -f "activate_jetson_env.sh" ]; then
    echo "  - activate_jetson_env.sh"
fi
echo ""
echo "利用可能なスクリプト:"
echo "  ./check_jetson_env.py       - 環境互換性チェック"
echo "  ./setup_jetson.sh           - 環境セットアップ"
echo "  ./create_directories.sh     - ディレクトリ構造作成"
echo "  ./start_jetson_server.sh    - サーバー起動"
echo "  ./test_jetson_setup.sh      - セットアップテスト"
if [ -f "activate_jetson_env.sh" ]; then
    echo "  source activate_jetson_env.sh - 環境アクティベート"
fi
echo ""
echo "⚠️  FileNotFoundErrorが発生した場合は:"
echo "   ./create_directories.sh を実行してください"
