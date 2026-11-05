FROM python:3.12-slim

WORKDIR /app

# Установка системных утилит
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

EXPOSE 5000

# Запуск миграций и веб-приложения
CMD ["sh", "-c", "python src/migrations/runner.py && python src/main.py"]
