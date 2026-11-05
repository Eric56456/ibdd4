"""
Конфигурация подключения к базе данных ConcertHub.
Считывает параметры окружения и предоставляет реквизиты по умолчанию.
"""

import os


class Config:
    # Параметры хоста и порта приложения
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "5000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

    # Параметры подключения к PostgreSQL
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "concerthub")

    # Суперпользователь БД для миграций и инициализации
    DB_ADMIN_USER: str = os.getenv("DB_ADMIN_USER", "postgres")
    DB_ADMIN_PASSWORD: str = os.getenv("DB_ADMIN_PASSWORD", "postgres")

    # Предустановленные тестовые учетные записи из ЛР №3
    DEFAULT_ACCOUNTS = {
        "ivan_customer": "customer",
        "petrov_staff": "staff",
        "admin_user": "admin",
        "postgres": "postgres",
    }

    # Секретный ключ для сессий Flask
    SECRET_KEY: str = os.getenv("SECRET_KEY", "concerthub-itmo-infosec-session-key-2026")


config = Config()
