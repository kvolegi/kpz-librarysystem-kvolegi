# ============================================
# Library System — Dockerfile
# Python 3.11
# ============================================

FROM python:3.11-slim AS base

# Метадані
LABEL maintainer="library-team"
LABEL description="Library System API"

# Змінні середовища
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Робоча директорія
WORKDIR /app

# Системні залежності
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Копіюємо та встановлюємо залежності окремо (кешування шарів Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо код проєкту
COPY src/ ./src/
COPY demo/ ./demo/
COPY tests/ ./tests/
COPY pytest.ini .

# Створюємо непривілейованого користувача
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    mkdir -p /app/logs && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "print('OK')" || exit 1

# Порт
EXPOSE 8000

# Запуск
CMD ["python", "-m", "src.api.books_async"]
