@echo off
setlocal enabledelayedexpansion

:: Edge Anomaly Detection System - タスクランナー

if "%1"=="" goto :help
if "%1"=="help" goto :help
if "%1"=="install" goto :install
if "%1"=="install-dev" goto :install-dev
if "%1"=="install-analysis" goto :install-analysis
if "%1"=="test" goto :test
if "%1"=="test-basic" goto :test-basic
if "%1"=="test-system" goto :test-system
if "%1"=="server" goto :server
if "%1"=="client" goto :client
if "%1"=="analyze" goto :analyze
if "%1"=="clean" goto :clean
if "%1"=="setup-dev" goto :setup-dev
goto :help

:help
echo Edge Anomaly Detection System - Available commands:
echo.
echo   install       - 基本依存関係をインストール
echo   install-dev   - 開発用依存関係をインストール
echo   install-analysis - 分析用依存関係をインストール
echo   test          - システムテストを実行
echo   test-basic    - 基本テストを実行
echo   test-system   - システムテストを実行
echo   server        - サーバを起動
echo   client        - クライアントを起動（デフォルトデバイス）
echo   analyze       - パフォーマンス分析を実行
echo   clean         - 生成ファイルをクリーンアップ
echo   setup-dev     - 開発環境をセットアップ
echo.
echo 使用例: tasks.bat install
goto :end

:install
echo 基本依存関係をインストール中...
pip install -r requirements.txt
goto :end

:install-dev
echo 開発用依存関係をインストール中...
pip install -r requirements-dev.txt
goto :end

:install-analysis
echo 分析用依存関係をインストール中...
pip install -r requirements-analysis.txt
goto :end

:test
echo システムテストを実行中...
call :test-basic
call :test-system
goto :end

:test-basic
echo 基本テストを実行中...
python basic_test.py
goto :end

:test-system
echo システムテストを実行中...
python test_system.py
goto :end

:server
echo サーバを起動中...
python server\main.py
goto :end

:client
echo クライアントを起動中...
set DEVICE_ID=%2
if "!DEVICE_ID!"=="" set DEVICE_ID=jetson-001
python edge\client.py --device-id !DEVICE_ID! --server-url http://localhost:8000
goto :end

:analyze
echo パフォーマンス分析を実行中...
if not exist "charts\" mkdir charts
python tools\performance_analyzer.py --data-dir .\data --output-report analysis_report.json --charts-dir .\charts
goto :end

:clean
echo 生成ファイルをクリーンアップ中...
if exist "__pycache__\" rmdir /s /q __pycache__
if exist ".pytest_cache\" rmdir /s /q .pytest_cache
if exist "build\" rmdir /s /q build
if exist "dist\" rmdir /s /q dist
for /r %%i in (*.egg-info) do if exist "%%i" rmdir /s /q "%%i"
for /r %%i in (*.pyc) do if exist "%%i" del "%%i"
if exist "logs\" for %%i in (logs\*.log) do if exist "%%i" del "%%i"
if exist "charts\" for %%i in (charts\*) do if exist "%%i" del "%%i"
echo クリーンアップ完了
goto :end

:setup-dev
echo 開発環境をセットアップ中...
if not exist "venv\" (
    echo 仮想環境を作成中...
    python -m venv venv
)
echo 仮想環境をアクティベート中...
call venv\Scripts\activate.bat
echo Pipをアップグレード中...
python -m pip install --upgrade pip
echo 開発用依存関係をインストール中...
pip install -r requirements-dev.txt
echo.
echo 開発環境のセットアップが完了しました！
echo 次に 'venv\Scripts\activate.bat' を実行して仮想環境をアクティベートしてください
goto :end

:end
endlocal
