"""
Главный модуль приложения ConcertHub (Лабораторная работа №4).
Реализует многопользовательский веб-интерфейс и REST API на базе Flask и SQLAlchemy ORM.
Поддерживает разграничение прав доступа на уровне ролей PostgreSQL:
- ivan_customer (Зритель / Customer)
- petrov_staff (Организатор / Staff)
- admin_user (Администратор / Admin)
"""

import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime, date

# Добавляем директорию src в пути поиска модулей
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, render_template, request, jsonify, session
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, ProgrammingError

from config import config
from database import get_session, test_connection
from migrations.runner import run_migrations
from repositories import (
    artist_repo,
    promoter_repo,
    venue_repo,
    hall_sector_repo,
    customer_repo,
    concert_repo,
    ticket_order_repo,
    ticket_repo,
    audit_repo,
    analytics_repo,
    REPOSITORIES_MAP,
)
from models import (
    ViewCustomerAfisha,
    ViewCustomerMyTickets,
    ViewPromoterSalesMonitoring,
    ViewPromoterGateControl,
    ViewArtistPopularity,
)

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Метаданные доступных таблиц и представлений для каждой роли (согласно заданию п. 3)
ROLE_PERMISSIONS = {
    "customer": {
        "title": "Зритель (ivan_customer)",
        "badge_color": "info",
        "description": "Доступ только к публичной афише, поиску мероприятий и личным билетам.",
        "allowed_tables": ["view_customer_afisha", "view_customer_my_tickets", "concert"],
        "editable_tables": [],
    },
    "staff": {
        "title": "Организатор / Персонал (petrov_staff)",
        "badge_color": "warning",
        "description": "Управление концертами, площадками, секторами, билетами и контроль входа.",
        "allowed_tables": [
            "concert",
            "ticket",
            "hall_sector",
            "venue",
            "artist",
            "promoter",
            "ticket_order",
            "customer",
            "view_promoter_sales_monitoring",
            "view_promoter_gate_control",
            "view_customer_afisha",
        ],
        "editable_tables": ["concert", "ticket", "hall_sector", "venue", "artist", "promoter"],
    },
    "admin": {
        "title": "Администратор (admin_user)",
        "badge_color": "danger",
        "description": "Полный доступ ко всем таблицам базы данных, журналу аудита и секретным данным.",
        "allowed_tables": [
            "artist",
            "promoter",
            "venue",
            "hall_sector",
            "customer",
            "concert",
            "ticket_order",
            "ticket",
            "view_customer_afisha",
            "view_customer_my_tickets",
            "view_promoter_sales_monitoring",
            "view_promoter_gate_control",
            "view_artist_popularity",
            "main_log",
            "secret_data",
        ],
        "editable_tables": [
            "artist", "promoter", "venue", "hall_sector",
            "customer", "concert", "ticket_order", "ticket"
        ],
    },
    "postgres": {
        "title": "Суперпользователь (postgres)",
        "badge_color": "dark",
        "description": "Полный системный доступ уровня суперпользователя СУБД.",
        "allowed_tables": [
            "artist", "promoter", "venue", "hall_sector", "customer", "concert",
            "ticket_order", "ticket", "view_customer_afisha", "view_customer_my_tickets",
            "view_promoter_sales_monitoring", "view_promoter_gate_control",
            "view_artist_popularity", "main_log", "secret_data",
        ],
        "editable_tables": [
            "artist", "promoter", "venue", "hall_sector",
            "customer", "concert", "ticket_order", "ticket"
        ],
    },
}

# Человекочитаемые названия сущностей
TABLE_TITLES = {
    "artist": "Исполнители (Artist)",
    "promoter": "Организаторы (Promoter)",
    "venue": "Концертные площадки (Venue)",
    "hall_sector": "Секторы зала (Hall_Sector)",
    "customer": "Зрители (Customer)",
    "concert": "Концерты (Concert)",
    "ticket_order": "Заказы билетов (Ticket_Order)",
    "ticket": "Билеты (Ticket)",
    "view_customer_afisha": "Представление: Афиша для зрителей",
    "view_customer_my_tickets": "Представление: Мои билеты",
    "view_promoter_sales_monitoring": "Представление: Мониторинг продаж",
    "view_promoter_gate_control": "Представление: Контроль на входе (Gate)",
    "view_artist_popularity": "Представление: Рейтинг артистов",
    "main_log": "Журнал аудита (audit.main_log)",
    "secret_data": "Секретные данные (audit.secret_data)",
}


def get_current_credentials():
    """Возвращает логин и пароль текущего активного пользователя из сессии."""
    user = session.get("user", "admin_user")
    pwd = session.get("password", config.DEFAULT_ACCOUNTS.get(user, "admin"))
    return user, pwd


def get_current_role(username: str) -> str:
    """Определяет роль пользователя."""
    if "admin" in username:
        return "admin"
    elif "staff" in username:
        return "staff"
    elif "customer" in username:
        return "customer"
    elif username == "postgres":
        return "postgres"
    return "customer"


def serialize_val(val):
    """Сериализация типов SQLAlchemy для JSON-ответов."""
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, (bytes, bytearray)):
        return f"\\x{val.hex()}"
    return val


# =========================================================================
# Страницы веб-интерфейса
# =========================================================================

@app.route("/")
def index():
    """Главная страница веб-интерфейса."""
    current_user, _ = get_current_credentials()
    current_role = get_current_role(current_user)
    role_info = ROLE_PERMISSIONS.get(current_role, ROLE_PERMISSIONS["customer"])
    return render_template(
        "index.html",
        current_user=current_user,
        current_role=current_role,
        role_info=role_info,
        table_titles=TABLE_TITLES,
    )


# =========================================================================
# API аутентификации и смены ролей
# =========================================================================

@app.route("/api/auth/login", methods=["POST"])
def login():
    """Вход под учетной записью пользователя PostgreSQL."""
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username:
        return jsonify({"success": False, "error": "Имя пользователя не может быть пустым"}), 400

    ok, msg = test_connection(username, password)
    if not ok:
        return jsonify({"success": False, "error": f"Ошибка подключения к PostgreSQL: {msg}"}), 401

    session["user"] = username
    session["password"] = password
    role = get_current_role(username)

    return jsonify({
        "success": True,
        "message": f"Вы успешно авторизованы как {username} (роль: {role})",
        "username": username,
        "role": role,
        "role_info": ROLE_PERMISSIONS.get(role, {}),
    })


@app.route("/api/auth/quick-switch", methods=["POST"])
def quick_switch():
    """Быстрое переключение между демонстрационными ролями."""
    data = request.json or {}
    target_role = data.get("role", "customer")

    role_to_user = {
        "customer": ("ivan_customer", "customer"),
        "staff": ("petrov_staff", "staff"),
        "admin": ("admin_user", "admin"),
        "postgres": ("postgres", config.DB_ADMIN_PASSWORD),
    }

    if target_role not in role_to_user:
        return jsonify({"success": False, "error": "Неизвестная роль"}), 400

    username, password = role_to_user[target_role]
    session["user"] = username
    session["password"] = password

    return jsonify({
        "success": True,
        "message": f"Сессия переключена на пользователя {username}",
        "username": username,
        "role": target_role,
        "role_info": ROLE_PERMISSIONS.get(target_role, {}),
    })


@app.route("/api/auth/current", methods=["GET"])
def current_user():
    """Информация о текущем аутентифицированном пользователе."""
    user, pwd = get_current_credentials()
    role = get_current_role(user)
    role_info = ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["customer"])
    return jsonify({
        "username": user,
        "role": role,
        "role_info": role_info,
        "available_tables": role_info["allowed_tables"],
        "editable_tables": role_info["editable_tables"],
    })


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    """Выход из учетной записи."""
    session.clear()
    return jsonify({"success": True, "message": "Сессия завершена"})


# =========================================================================
# API таблиц: динамический список, отображение, добавление, удаление (п. 1-3)
# =========================================================================

@app.route("/api/tables", methods=["GET"])
def list_tables():
    """Возвращает список доступных таблиц для текущей роли (п. 3 задания)."""
    user, _ = get_current_credentials()
    role = get_current_role(user)
    allowed = ROLE_PERMISSIONS.get(role, {}).get("allowed_tables", [])
    editable = ROLE_PERMISSIONS.get(role, {}).get("editable_tables", [])

    tables_info = []
    for t_name in allowed:
        tables_info.append({
            "name": t_name,
            "title": TABLE_TITLES.get(t_name, t_name),
            "is_editable": t_name in editable,
            "is_view": t_name.startswith("view_"),
        })

    return jsonify({
        "role": role,
        "user": user,
        "tables": tables_info,
    })


@app.route("/api/data/<table_name>", methods=["GET"])
def get_table_data(table_name: str):
    """Получение данных таблицы с фильтрацией, сортировкой и пагинацией."""
    user, pwd = get_current_credentials()
    role = get_current_role(user)

    # Проверка прав на уровне приложения
    allowed_tables = ROLE_PERMISSIONS.get(role, {}).get("allowed_tables", [])
    if table_name not in allowed_tables:
        return jsonify({
            "error": f"Доступ запрещен. Роль '{role}' не имеет привилегий для просмотра таблицы '{table_name}'.",
            "code": "ACCESS_DENIED_APP_ROLE",
        }), 403

    limit = int(request.args.get("limit", 100))
    offset = int(request.args.get("offset", 0))
    sort_by = request.args.get("sort_by")
    sort_order = request.args.get("sort_order", "asc")
    search = request.args.get("search", "").strip()

    try:
        db = get_session(user, pwd)
        try:
            # 1. Если это представление
            view_classes = {
                "view_customer_afisha": ViewCustomerAfisha,
                "view_customer_my_tickets": ViewCustomerMyTickets,
                "view_promoter_sales_monitoring": ViewPromoterSalesMonitoring,
                "view_promoter_gate_control": ViewPromoterGateControl,
                "view_artist_popularity": ViewArtistPopularity,
            }

            if table_name in view_classes:
                view_cls = view_classes[table_name]
                query = db.query(view_cls)
                rows = query.offset(offset).limit(limit).all()
                data = [r.to_dict() for r in rows]
                columns = [c.name for c in view_cls.__table__.columns]
                return jsonify({"table": table_name, "columns": columns, "data": data, "count": len(data)})

            # 2. Если это таблица аудита main_log
            if table_name == "main_log":
                logs = audit_repo.get_logs(db, limit=limit)
                cols = ["log_item_id", "operation_type", "operation_date", "user_operator", "changed_data"]
                return jsonify({"table": table_name, "columns": cols, "data": logs, "count": len(logs)})

            # 3. Если это таблица секретных данных secret_data
            if table_name == "secret_data":
                secrets = audit_repo.get_secrets(db)
                cols = ["ID", "username", "secret_token"]
                return jsonify({"table": table_name, "columns": cols, "data": secrets, "count": len(secrets)})

            # 4. Базовые таблицы ORM
            if table_name in REPOSITORIES_MAP:
                repo = REPOSITORIES_MAP[table_name]
                filters = {}
                rows = repo.get_all(db, limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order, filters=filters)
                data = [r.to_dict() for r in rows]
                columns = [c.name for c in repo.model.__table__.columns]
                return jsonify({"table": table_name, "columns": columns, "data": data, "count": len(data)})

            return jsonify({"error": f"Неизвестная сущность {table_name}"}), 404

        finally:
            db.close()

    except DBAPIError as exc:
        # Перехватываем исключение СУБД (например, InsufficientPrivilege)
        err_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)
        return jsonify({
            "error": f"Ошибка СУБД PostgreSQL (psycopg2.errors.InsufficientPrivilege):\n{err_msg}",
            "code": "DB_INSUFFICIENT_PRIVILEGE",
        }), 403
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/data/<table_name>", methods=["POST"])
def create_record(table_name: str):
    """Добавление новой записи в таблицу через ORM (п. 1 задания)."""
    user, pwd = get_current_credentials()
    role = get_current_role(user)

    editable_tables = ROLE_PERMISSIONS.get(role, {}).get("editable_tables", [])
    if table_name not in editable_tables:
        return jsonify({
            "error": f"Отказ в доступе: роль '{role}' не имеет права на добавление записей в таблицу '{table_name}'.",
        }), 403

    if table_name not in REPOSITORIES_MAP:
        return jsonify({"error": f"Таблица '{table_name}' не поддерживает операцию добавления"}), 400

    data = request.json or {}
    try:
        db = get_session(user, pwd)
        try:
            repo = REPOSITORIES_MAP[table_name]
            obj = repo.create(db, data)
            return jsonify({
                "success": True,
                "message": f"Запись успешно добавлена в таблицу '{table_name}'. Сработал триггер аудита.",
                "data": obj.to_dict(),
            }), 201
        finally:
            db.close()
    except DBAPIError as exc:
        err_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)
        return jsonify({"error": f"Ошибка СУБД: {err_msg}"}), 403
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/data/<table_name>/<int:record_id>", methods=["DELETE"])
def delete_record(table_name: str, record_id: int):
    """Удаление записи из таблицы через ORM (п. 1 задания)."""
    user, pwd = get_current_credentials()
    role = get_current_role(user)

    editable_tables = ROLE_PERMISSIONS.get(role, {}).get("editable_tables", [])
    if table_name not in editable_tables:
        return jsonify({
            "error": f"Отказ в доступе: роль '{role}' не имеет права на удаление записей из таблицы '{table_name}'.",
        }), 403

    if table_name not in REPOSITORIES_MAP:
        return jsonify({"error": f"Таблица '{table_name}' не поддерживает операцию удаления"}), 400

    try:
        db = get_session(user, pwd)
        try:
            repo = REPOSITORIES_MAP[table_name]
            deleted = repo.delete(db, record_id)
            if not deleted:
                return jsonify({"error": f"Запись с ID {record_id} не найдена"}), 404
            return jsonify({
                "success": True,
                "message": f"Запись ID {record_id} успешно удалена из таблицы '{table_name}'. Изменение зафиксировано в audit.main_log.",
            })
        finally:
            db.close()
    except DBAPIError as exc:
        err_msg = str(exc.orig) if hasattr(exc, "orig") else str(exc)
        return jsonify({"error": f"Ошибка СУБД: {err_msg}"}), 403
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# =========================================================================
# API сложных аналитических запросов с GROUP BY (п. 4 задания)
# =========================================================================

@app.route("/api/analytics/customer", methods=["GET"])
def analytics_customer():
    """
    Сложный SQL-запрос для роли Зрителя (Customer).
    Сущности: Concert + Artist + Venue + Ticket (4 сущности).
    Группировка: по концертам, площадкам и артистам.
    Агрегаты: COUNT(доступные билеты), MIN(цена), MAX(цена), AVG(цена).
    """
    user, pwd = get_current_credentials()
    city = request.args.get("city")
    genre = request.args.get("genre")
    max_price = request.args.get("max_price", type=float)
    sort_by = request.args.get("sort_by", "start_datetime")
    sort_order = request.args.get("sort_order", "asc")

    try:
        db = get_session(user, pwd)
        try:
            results = analytics_repo.get_customer_afisha_summary(
                db, city=city, genre=genre, max_price=max_price, sort_by=sort_by, sort_order=sort_order
            )
            return jsonify({
                "role": "customer",
                "title": "Сводка афиши и доступности билетов (GROUP BY c.concert_id, a.stage_name, v.venue_name)",
                "data": results,
                "count": len(results),
            })
        finally:
            db.close()
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/analytics/staff", methods=["GET"])
def analytics_staff():
    """
    Сложный SQL-запрос для роли Персонала / Организатора (Staff).
    Сущности: Concert + Promoter + Artist + Venue + Ticket (5 сущностей).
    Группировка: по промоутерам, концертам, площадкам.
    Агрегаты: COUNT(проданные билеты), процент заполняемости, выручка, средняя цена билета.
    """
    user, pwd = get_current_credentials()
    role = get_current_role(user)

    if role not in ("staff", "admin", "postgres"):
        return jsonify({"error": f"Доступ к аналитике организаторов запрещен для роли '{role}'"}), 403

    promoter = request.args.get("promoter")
    min_revenue = request.args.get("min_revenue", type=float)
    sort_by = request.args.get("sort_by", "total_revenue")
    sort_order = request.args.get("sort_order", "desc")

    try:
        db = get_session(user, pwd)
        try:
            results = analytics_repo.get_staff_sales_monitoring(
                db, promoter=promoter, min_revenue=min_revenue, sort_by=sort_by, sort_order=sort_order
            )
            return jsonify({
                "role": "staff",
                "title": "Мониторинг сборов и заполняемости площадок (GROUP BY p.company_name, c.concert_id, v.venue_name)",
                "data": results,
                "count": len(results),
            })
        finally:
            db.close()
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/analytics/admin", methods=["GET"])
def analytics_admin():
    """
    Сложный SQL-запрос для роли Администратора (Admin).
    Сущности: Artist + Concert + Venue + Ticket (4 сущности).
    Группировка: по артистам и музыкальным жанрам.
    Агрегаты: общее число концертов, охват городов, проданные билеты, валовая выручка, средний доход за шоу.
    """
    user, pwd = get_current_credentials()
    role = get_current_role(user)

    if role not in ("admin", "postgres"):
        return jsonify({"error": f"Доступ к административной аналитике запрещен для роли '{role}'"}), 403

    genre = request.args.get("genre")
    min_tickets = request.args.get("min_tickets", type=int)
    sort_by = request.args.get("sort_by", "total_gross")
    sort_order = request.args.get("sort_order", "desc")

    try:
        db = get_session(user, pwd)
        try:
            results = analytics_repo.get_admin_artist_stats(
                db, genre=genre, min_tickets=min_tickets, sort_by=sort_by, sort_order=sort_order
            )
            audit_stats = analytics_repo.get_admin_audit_activity(db)
            return jsonify({
                "role": "admin",
                "title": "Коммерческая статистика артистов и география туров (GROUP BY a.artist_id, a.stage_name, a.music_genre)",
                "data": results,
                "audit_summary": audit_stats,
                "count": len(results),
            })
        finally:
            db.close()
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# =========================================================================
# API расшифровки секретных токенов (демонстрация pgcrypto из ЛР №3)
# =========================================================================

@app.route("/api/audit/decrypt", methods=["POST"])
def decrypt_token():
    """Расшифровка токена из audit.secret_data с использованием pgp_sym_decrypt."""
    user, pwd = get_current_credentials()
    role = get_current_role(user)

    if role not in ("admin", "postgres"):
        return jsonify({"error": "Доступ к секретным ключам имеет только администратор."}), 403

    data = request.json or {}
    record_id = int(data.get("id", 1))
    key = data.get("key", "29aaa1424afb8e8c740fb247a9d44723c8b5c82d8a12994ee2ed8b64e4410b63")

    try:
        db = get_session(user, pwd)
        try:
            decrypted = audit_repo.decrypt_secret(db, record_id, key)
            if not decrypted:
                return jsonify({"error": "Запись не найдена"}), 404
            return jsonify({
                "success": True,
                "data": decrypted,
                "message": "Токен успешно расшифрован функцией pgp_sym_decrypt() СУБД PostgreSQL.",
            })
        finally:
            db.close()
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


# =========================================================================
# Запуск приложения
# =========================================================================

if __name__ == "__main__":
    print(f"[*] Запуск сервера ConcertHub на http://{config.APP_HOST}:{config.APP_PORT}")
    app.run(host=config.APP_HOST, port=config.APP_PORT, debug=config.DEBUG)
