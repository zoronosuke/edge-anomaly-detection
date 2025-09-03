@echo off
echo 🚀 Edge Anomaly Detection System - Server起動

cd /d "%~dp0"

REM Python仮想環境のアクティベート（存在する場合）
if exist "venv\Scripts\activate.bat" (
    echo 📦 仮想環境をアクティベート
    call venv\Scripts\activate.bat
)

REM 環境変数ファイルのコピー（初回のみ）
if not exist ".env" (
    if exist ".env.example" (
        echo ⚙️ 環境変数ファイルをコピー
        copy ".env.example" ".env"
        echo ⚠️ .envファイルを編集してLINE設定などを行ってください
        pause
    )
)

REM 必要なディレクトリの作成
if not exist "data" mkdir data
if not exist "data\images" mkdir "data\images"

REM サーバー起動
echo 🌐 FastAPIサーバーを起動中...
cd server
python main.py

pause
