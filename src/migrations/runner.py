"""
Модуль запуска миграций базы данных ConcertHub.
Считывает SQL-файлы из директории versions/ и применяет их последовательно к БД от имени суперпользователя postgres.
"""

from pathlib import Path
from sqlalchemy import create_engine, text
from config import config


def run_migrations(admin_user: str = None, admin_password: str = None) -> None:
    """Применяет версионированные SQL миграции к целевой базе данных."""
    user = admin_user or config.DB_ADMIN_USER
    pwd = admin_password or config.DB_ADMIN_PASSWORD
    db_url = f"postgresql+psycopg2://{user}:{pwd}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"

    engine = create_engine(db_url, isolation_level="AUTOCOMMIT")
    versions_dir = Path(__file__).parent / "versions"
    sql_files = sorted(versions_dir.glob("*.sql"))

    with engine.connect() as conn:
        for sql_file in sql_files:
            print(f"[Migration] Применение миграции: {sql_file.name}")
            with open(sql_file, "r", encoding="utf-8") as f:
                content = f.read()
            # Выполняем SQL скрипт целиком
            conn.execute(text(content))
        print("[Migration] Все миграции успешно выполнены.")

    engine.dispose()


if __name__ == "__main__":
    run_migrations()
