# Makefile for Edge Anomaly Detection System
# Windows環境用（PowerShell）とJetson環境対応

.PHONY: help install install-dev install-analysis clean test server client analyze docker setup-jetson install-jetson check-jetson jetson-server jetson-client

# デフォルトターゲット
help:
	@echo "Edge Anomaly Detection System - Available commands:"
	@echo ""
	@echo "=== Windows環境（サーバー側）==="
	@echo "  install       - 基本依存関係をインストール"
	@echo "  install-dev   - 開発用依存関係をインストール"
	@echo "  install-analysis - 分析用依存関係をインストール"
	@echo "  server        - サーバを起動"
	@echo "  test          - システムテストを実行"
	@echo "  test-basic    - 基本テストを実行"
	@echo "  analyze       - パフォーマンス分析を実行"
	@echo "  clean         - 生成ファイルをクリーンアップ"
	@echo ""
	@echo "=== エッジデバイス（Jetson）環境 ==="
	@echo "  setup-jetson  - Jetson環境を自動セットアップ"
	@echo "  install-jetson - Jetson用依存関係をインストール"
	@echo "  check-jetson  - Jetson環境をチェック"
	@echo "  jetson-client - Jetsonクライアントを起動"
	@echo "  jetson-test   - Jetson環境でテスト実行"
	@echo ""
	@echo "=== Docker関連 ==="
	@echo "  docker-build  - Dockerイメージをビルド"
	@echo "  docker-run    - Dockerコンテナを実行"

# 依存関係インストール
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

install-analysis:
	pip install -r requirements-analysis.txt

# テスト
test: test-basic test-system

test-basic:
	python basic_test.py

test-system:
	python test_system.py

# サーバ・クライアント起動
server:
	python server/main.py

client:
	python edge/client.py --device-id windows-001 --server-url http://localhost:8000

# 分析
analyze:
	python tools/performance_analyzer.py --data-dir ./data --output-report analysis_report.json --charts-dir ./charts

# クリーンアップ
clean:
	-Remove-Item -Recurse -Force __pycache__
	-Remove-Item -Recurse -Force *.pyc
	-Remove-Item -Recurse -Force .pytest_cache
	-Remove-Item -Recurse -Force build
	-Remove-Item -Recurse -Force dist
	-Remove-Item -Recurse -Force *.egg-info
	-Remove-Item -Force logs/*.log
	-Remove-Item -Force charts/*

# Docker関連
docker-build:
	docker build -t edge-anomaly-detection .

docker-run:
	docker run -p 8000:8000 -v ${PWD}/data:/app/data -v ${PWD}/logs:/app/logs edge-anomaly-detection

# 開発環境セットアップ
setup-dev:
	python -m venv venv
	./venv/Scripts/activate.ps1
	pip install --upgrade pip
	pip install -r requirements-dev.txt
	@echo "開発環境のセットアップが完了しました"
	@echo "次に './venv/Scripts/activate.ps1' を実行して仮想環境をアクティベートしてください"

# === Jetson環境用ターゲット ===

# Jetson環境の自動セットアップ
setup-jetson:
	@echo "Jetson環境のセットアップを開始します..."
	bash setup_jetson.sh

# Jetson用依存関係インストール（競合解決版）
install-jetson:
	@echo "Jetson用パッケージをインストールしています..."
	pip install --upgrade pip
	pip install --upgrade "numpy>=1.22.2"
	pip install fastapi uvicorn aiofiles requests python-dotenv pillow opencv-python
	pip install "ultralytics>=8.0.200" --no-deps
	pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Jetson環境チェック
check-jetson:
	@echo "=== Jetson環境の確認 ==="
	@echo "Python: $$(python --version)"
	@echo "numpy: $$(python -c 'import numpy; print(numpy.__version__)' 2>/dev/null || echo 'not installed')"
	@echo "ultralytics: $$(python -c 'import ultralytics; print(ultralytics.__version__)' 2>/dev/null || echo 'not installed')"
	@echo "torch: $$(python -c 'import torch; print(torch.__version__)' 2>/dev/null || echo 'not installed')"
	@echo "opencv: $$(python -c 'import cv2; print(cv2.__version__)' 2>/dev/null || echo 'not installed')"
	@echo "fastapi: $$(python -c 'import fastapi; print(fastapi.__version__)' 2>/dev/null || echo 'not installed')"
	@echo "=== GPU確認 ==="
	@echo "CUDA available: $$(python -c 'import torch; print(torch.cuda.is_available())' 2>/dev/null || echo 'torch not available')"

# Jetsonクライアント起動
jetson-client:
	@echo "Jetsonクライアントを起動します..."
	python edge/client.py --device-id jetson-nano-001 --server-url http://192.168.1.100:8000

# Jetsonサーバー起動（エッジでサーバーを動かす場合）
jetson-server:
	@echo "Jetsonサーバーを起動します..."
	python server/main.py --host 0.0.0.0 --port 8000

# Jetson環境でのテスト
jetson-test:
	@echo "Jetson環境でテストを実行します..."
	python basic_test.py
	python check_jetson_env.py

# Jetson環境のクリーンアップ
clean-jetson:
	@echo "Jetson環境をクリーンアップしています..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache 2>/dev/null || true
	rm -f logs/*.log 2>/dev/null || true

# Jetson用仮想環境の作成
setup-jetson-venv:
	@echo "Jetson用仮想環境を作成します..."
	python3.8 -m venv ~/venv-jetson-py38
	@echo "仮想環境が作成されました: ~/venv-jetson-py38"
	@echo "アクティベート: source ~/venv-jetson-py38/bin/activate"

# 環境アクティベート確認
activate-jetson:
	@echo "環境をアクティベートします..."
	bash -c "source activate_jetson_env.sh && python --version"
