# Makefile for Edge Anomaly Detection System
# Windows環境用（PowerShell）

.PHONY: help install install-dev install-analysis clean test server client analyze docker

# デフォルトターゲット
help:
	@echo "Edge Anomaly Detection System - Available commands:"
	@echo ""
	@echo "  install       - 基本依存関係をインストール"
	@echo "  install-dev   - 開発用依存関係をインストール"
	@echo "  install-analysis - 分析用依存関係をインストール"
	@echo "  test          - システムテストを実行"
	@echo "  test-basic    - 基本テストを実行"
	@echo "  server        - サーバを起動"
	@echo "  client        - クライアントを起動（デフォルトデバイス）"
	@echo "  analyze       - パフォーマンス分析を実行"
	@echo "  clean         - 生成ファイルをクリーンアップ"
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
	python edge/client.py --device-id jetson-001 --server-url http://localhost:8000

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
