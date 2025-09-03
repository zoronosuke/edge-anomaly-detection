@echo off
echo 🧪 Edge Client (Dummy) 起動

cd /d "%~dp0"

REM Python仮想環境のアクティベート（存在する場合）
if exist "venv\Scripts\activate.bat" (
    echo 📦 仮想環境をアクティベート
    call venv\Scripts\activate.bat
)

cd client

REM デフォルト設定でダミークライアント起動
echo 🤖 ダミークライアントを起動中...
echo    サーバー: http://localhost:8000
echo    デバイスID: dummy-test
echo    FPS: 1.0
echo    実行時間: 60秒
echo.

python dummy_client.py --device-id dummy-test --duration 60

pause
