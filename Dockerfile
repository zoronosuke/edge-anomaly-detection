FROM python:3.9-slim

WORKDIR /app

# システム依存関係をインストール
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    libgtk-3-0 \
    libcairo-gobject2 \
    libgtk-3-dev \
    libgdk-pixbuf2.0-dev \
    libpango1.0-dev \
    libatk1.0-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY server/ ./server/
COPY config.json .
COPY .env.example .env

# データとログディレクトリを作成
RUN mkdir -p data logs

# ポート公開
EXPOSE 8000

# サーバを起動
CMD ["python", "server/main.py"]
