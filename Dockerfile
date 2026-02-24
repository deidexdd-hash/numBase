# ================================================================
# Dockerfile — Нумерология и Ансестология v3.0
# Образ: python:3.11-slim (~150MB)
# Порт: 8000
#
# Сборка:
#   docker build -t numerology-app .
#
# Запуск:
#   docker run -p 8000:8000 -e OPENAI_API_KEY=sk-... numerology-app
#
# С данными (volume):
#   docker run -p 8000:8000 \
#     -v $(pwd)/data:/app/data \
#     -e OPENAI_API_KEY=sk-... \
#     numerology-app
# ================================================================

FROM python:3.11-slim

# Метаданные
LABEL maintainer="project"
LABEL version="3.0"
LABEL description="Numerology & Ancestology Knowledge Base"

# Рабочая директория
WORKDIR /app

# Системные зависимости (минимальный набор)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Зависимости Python (сначала — кэшируются если не изменились)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        fastapi==0.115.6 \
        uvicorn[standard]==0.32.1 \
        aiofiles==24.1.0 \
        python-multipart==0.0.12 \
        openai>=1.50.0 \
        python-telegram-bot==20.7 \
        beautifulsoup4==4.12.3 \
        lxml==5.3.0 \
        python-dotenv==1.0.1 \
        requests==2.32.5

# Исходный код приложения
COPY . .

# Создаём директорию данных если не существует
RUN mkdir -p /app/data /app/app

# Переменные окружения (можно переопределить при запуске)
ENV HOST=0.0.0.0
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Открываем порт
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Запуск через uvicorn напрямую (без webbrowser.open в Docker)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
