"""
Модуль управления подключениями к PostgreSQL с использованием SQLAlchemy.
Реализует динамическое создание сессий для различных ролей БД (ivan_customer, petrov_staff, admin_user).
"""

from typing import Dict
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import NullPool

from config import config

Base = declarative_base()

# Кэш пулов соединений для разных пользователей БД
_engines: Dict[str, any] = {}


def get_db_url(username: str, password: str) -> str:
    """Формирует строку подключения PostgreSQL для указанного пользователя."""
    encoded_user = quote_plus(username)
    encoded_pwd = quote_plus(password)
    return (
        f"postgresql+psycopg2://{encoded_user}:{encoded_pwd}@"
        f"{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
    )


def get_engine(username: str, password: str):
    """Возвращает или создает SQLAlchemy Engine для конкретного пользователя БД."""
    key = f"{username}:{password}"
    if key not in _engines:
        url = get_db_url(username, password)
        _engines[key] = create_engine(
            url,
            poolclass=NullPool, # Отключаем постоянный пул, чтобы оперативно реагировать на смену роли
            echo=False,
        )
    return _engines[key]


def get_session(username: str, password: str) -> Session:
    """Создает сессию SQLAlchemy от имени указанной учетной записи PostgreSQL."""
    engine = get_engine(username, password)
    SessionMaker = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return SessionMaker()


def test_connection(username: str, password: str) -> tuple[bool, str]:
    """Проверяет возможность подключения к БД с переданными реквизитами."""
    try:
        engine = get_engine(username, password)
        with engine.connect() as conn:
            from sqlalchemy import text
            res = conn.execute(text("SELECT current_user, current_database();")).fetchone()
            return True, f"Успешное подключение. Пользователь: {res[0]}, БД: {res[1]}"
    except Exception as exc:
        return False, str(exc)
