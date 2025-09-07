@echo off
REM クイックスタートスクリプト - Edge Anomaly Detection System (Windows)

echo 🚀 Edge Anomaly Detection System - Quick Start (Windows)
echo ===========================================================
echo.

echo 🪟 Windows環境を検出しました
echo.

REM Pythonの確認
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Pythonが見つかりません
    echo    https://www.python.org/downloads/ からPythonをインストールしてください
    pause
    exit /b 1
)

echo ✅ Python: 
python --version

echo.
echo セットアップオプション:
echo 1. 自動セットアップ（推奨）
echo 2. 手動セットアップ
echo 3. 既存環境でサーバー起動
echo.

set /p choice=選択してください [1-3]: 

if "%choice%"=="1" (
    echo.
    echo 🔧 自動セットアップを実行中...
    if exist tasks.bat (
        call tasks.bat setup-dev
    ) else (
        echo ❌ tasks.bat が見つかりません
        echo 手動セットアップに切り替えます...
        goto manual_setup
    )
    goto complete
)

if "%choice%"=="2" (
    goto manual_setup
)

if "%choice%"=="3" (
    goto start_server
)

echo ❌ 無効な選択です
pause
exit /b 1

:manual_setup
echo.
echo 🔧 手動セットアップを実行中...

REM 仮想環境の作成
if not exist venv (
    echo 仮想環境を作成中...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 仮想環境の作成に失敗しました
        pause
        exit /b 1
    )
)

echo 仮想環境をアクティベート中...
call venv\Scripts\activate.bat

echo 依存関係をインストール中...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ⚠️  依存関係のインストールで問題が発生しました
    echo 個別パッケージのインストールを試行中...
    pip install fastapi uvicorn aiofiles requests ultralytics opencv-python
)

echo.
echo 設定ファイルを準備中...
if not exist .env (
    if exist .env.example (
        copy .env.example .env >nul
        echo ✅ .envファイルを作成しました
        echo ⚠️  .envファイルを編集して設定を調整してください
        echo    notepad .env
    ) else (
        echo ⚠️  .env.exampleが見つかりません
    )
) else (
    echo ✅ .envファイルは既に存在します
)

goto complete

:start_server
echo.
echo 🚀 サーバーを起動中...

if exist start_server.bat (
    call start_server.bat
) else (
    if exist venv\Scripts\activate.bat (
        call venv\Scripts\activate.bat
        python server\main.py
    ) else (
        python server\main.py
    )
)
goto end

:complete
echo.
echo ✅ セットアップ完了！
echo.
echo 次のステップ:
echo 1. 設定ファイルの編集:
echo    notepad .env
echo.
echo 2. サーバーの起動:
echo    start_server.bat
echo.
echo 3. クライアントの起動 (別のコマンドプロンプト):
echo    start_client.bat --device-id windows-pc-001
echo.
echo 4. ブラウザでの確認:
echo    http://localhost:8000
echo.

set /p start_now=今すぐサーバーを起動しますか? [y/N]: 
if /i "%start_now%"=="y" (
    goto start_server
)

:end
echo.
echo 📚 詳細な手順: SETUP_GUIDE.md
echo 🐛 問題が発生した場合:
echo    - README.md のトラブルシューティング
echo    - logs\server.log ファイル
echo    - GitHub Issues: https://github.com/zoronosuke/edge-anomaly-detection/issues
echo.
echo 🎉 Happy coding!
echo.
pause
