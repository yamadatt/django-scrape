FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Chrome for Seleniumをインストール（ARM64対応）
RUN apt-get update \
    && apt-get install -y chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Pythonの依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードをコピー
COPY . .

# ポート8000を公開
EXPOSE 8000

# 環境変数を設定
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=scraping_project.settings

# Djangoアプリケーションを起動
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "scraping_project.wsgi:application"] 