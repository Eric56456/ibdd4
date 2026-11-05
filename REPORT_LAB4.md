# МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ РОССИЙСКОЙ ФЕДЕРАЦИИ
## ФЕДЕРАЛЬНОЕ ГОСУДАРСТВЕННОЕ АВТОНОМНОЕ ОБРАЗОВАТЕЛЬНОЕ УЧРЕЖДЕНИЕ ВЫСШЕГО ОБРАЗОВАНИЯ
# «НАЦИОНАЛЬНЫЙ ИССЛЕДОВАТЕЛЬСКИЙ УНИВЕРСИТЕТ ИТМО»

### Факультет безопасности информационных технологий
**Направление подготовки:** Технологии защиты информации  
**Образовательная программа:** Информационная безопасность  
**Дисциплина:** «Информационная безопасность баз данных»  

<br><br><br>

# ОТЧЕТ ПО ЛАБОРАТОРНОЙ РАБОТЕ №4
### «Реализация уровня приложения с возможностью многопользовательского доступа к созданной БД»

<br><br><br>

**Выполнили студенты:**  
группа/поток N3345, N3346  
- Сушко Руслан Леонидович  
- Мавлявиев Эрик Рустамович  
- Назмиев Марат Ильшатович  

**Проверила:**  
Ярцева Наталия Андреевна  

<br><br>
**Санкт-Петербург**  
**2026г.**

---

## ВВЕДЕНИЕ

### Цель работы:
Получение практических навыков использования серверных языков программирования, ORM-систем и веб-фреймворков для реализации прикладного уровня информационной системы продажи билетов и афиши концертов «ConcertHub», а также построение механизмов многопользовательского ролевого доступа к реляционной СУБД PostgreSQL.

### Задачи работы:
1. Выбрать и обосновать программный стек для реализации пользовательского интерфейса (язык программирования, среду разработки, веб-фреймворк и ORM-библиотеку).
2. Выполнить объектно-реляционный маппинг (ORM) таблиц и представлений базы данных «ConcertHub», спроектированных в лабораторных работах №1–3, в структуру классов.
3. Разработать пользовательский интерфейс с возможностью многопользовательского разграничения доступа к данным из БД под учетными записями, выделенными в ЛР №3 (`ivan_customer`, `petrov_staff`, `admin_user`, `postgres`).
4. Обеспечить динамическое формирование списка таблиц и представлений, доступных для просмотра и редактирования каждому типу пользователей.
5. Для каждой группы пользователей составить и внедрить в интерфейс сложный SQL-запрос с использованием данных более чем из 2 сущностей и функции агрегации `GROUP BY`, с поддержкой интерактивной сортировки и фильтрации.
6. Продемонстрировать корректность работы системы аудита (триггеры на вставку/изменение/удаление данных) и механизмов криптографической защиты (`pgcrypto`).

---

## 1. Обоснование выбора среды программирования и фреймворков

Для разработки уровня приложения информационной системы «ConcertHub» был выбран стек технологий на базе языка **Python**:

1. **Язык программирования:** Python 3.12 / 3.13. Язык обладает развитой экосистемой библиотек для работы с базами данных, строгой типизацией моделей и высокой скоростью разработки.
2. **Среда разработки (IDE):** PyCharm Professional / VS Code, предоставляющие инструменты отладки, инспекции SQL-запросов и интеграции с СУБД.
3. **ORM-система:** **SQLAlchemy 2.0**. Библиотека предоставляет паттерны Data Mapper и Active Record, строгую типизацию сущностей, автоматическое управление транзакциями и эффективное экранирование параметров, защищающее от SQL-инъекций.
4. **Драйвер подключения к СУБД:** **psycopg2** / **psycopg2-binary** — стандартный высокопроизводительный адаптер протокола PostgreSQL для Python с поддержкой SSL и нативных типов данных.
5. **Веб-фреймворк:** **Flask** — легковесный WSGI-фреймворк, позволяющий гибко управлять жизненным циклом сессий СУБД, реализовать динамическую авторизацию под разными ролями PostgreSQL и предоставить отзывчивый веб-интерфейс.

### Установка зависимостей:
```bash
pip install sqlalchemy psycopg2-binary flask pydantic
```

---

## 2. Архитектура программной реализации

Проект организован по модульному принципу в соответствии с единой хронологией лабораторных работ:

- `src/config.py` — централизованная конфигурация подключения к базе данных;
- `src/database.py` — фабрика сессий SQLAlchemy, обеспечивающая динамическое подключение к PostgreSQL под учетными записями конкретных пользователей (`get_session(user, password)`);
- `src/models/` — ORM-маппинг сущностей предметной области (`Artist`, `Concert`, `Customer`, `Promoter`, `Venue`, `HallSector`, `TicketOrder`, `Ticket`), представлений (`ViewCustomerAfisha`, `ViewPromoterSalesMonitoring` и др.) и схемы безопасности `audit`;
- `src/repositories/` — слой репозиториев, реализующий операции CRUD и сложные аналитические запросы к СУБД;
- `src/migrations/` — подсистема версионированных SQL-скриптов создания схемы (`01_create_tables.sql`) и наполнения тестовыми данными (`02_seed_data.sql`);
- `src/templates/` и `src/static/` — клиентский веб-интерфейс на HTML5, CSS3 и JavaScript.

---

## 3. Маппинг структуры базы данных в классы ORM SQLAlchemy

Для сопоставления реляционных таблиц классам языка Python используется декларативная база `Base = declarative_base()`. Ниже приведены фрагменты маппинга ключевых сущностей:

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

def get_engine(username: str, password: str):
    url = f"postgresql+psycopg2://{username}:{password}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
    return create_engine(url, pool_pre_ping=True)

def get_session(username: str, password: str):
    engine = get_engine(username, password)
    SessionMaker = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return SessionMaker()
```

### Модели основных таблиц (схема public):

```python
# models/artist.py
from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import relationship
from database import Base

class Artist(Base):
    __tablename__ = "artist"
    artist_id = Column(Integer, primary_key=True, autoincrement=True)
    stage_name = Column(Text, nullable=False)
    leader_full_name = Column(Text, nullable=True)
    music_genre = Column(Text, nullable=True)
    concerts = relationship("Concert", back_populates="artist", cascade="all, delete-orphan")

# models/concert.py
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Concert(Base):
    __tablename__ = "concert"
    concert_id = Column(Integer, primary_key=True, autoincrement=True)
    program_name = Column(Text, nullable=False)
    start_datetime = Column(DateTime, nullable=False)
    age_restriction = Column(Text, nullable=True)
    artist_id = Column(Integer, ForeignKey("artist.artist_id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    venue_id = Column(Integer, ForeignKey("venue.venue_id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    promoter_id = Column(Integer, ForeignKey("promoter.promoter_id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)

    artist = relationship("Artist", back_populates="concerts")
    venue = relationship("Venue", back_populates="concerts")
    promoter = relationship("Promoter", back_populates="concerts")
    tickets = relationship("Ticket", back_populates="concert", cascade="all, delete-orphan")

# models/customer.py
from sqlalchemy import Column, Integer, Text, Date
from sqlalchemy.orm import relationship
from database import Base

class Customer(Base):
    __tablename__ = "customer"
    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_full_name = Column(Text, nullable=False)
    email = Column(Text, unique=True, nullable=True)
    phone_number = Column(Text, nullable=True)
    birth_date = Column(Date, nullable=True)
    orders = relationship("TicketOrder", back_populates="customer", cascade="all, delete-orphan")

# models/ticket.py
from sqlalchemy import Column, Integer, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from database import Base

class Ticket(Base):
    __tablename__ = "ticket"
    ticket_id = Column(Integer, primary_key=True, autoincrement=True)
    barcode = Column(Text, unique=True, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    ticket_status = Column(Text, nullable=False) # 'Доступен', 'Продан', 'Аннулирован'
    concert_id = Column(Integer, ForeignKey("concert.concert_id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    sector_id = Column(Integer, ForeignKey("hall_sector.sector_id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    order_id = Column(Integer, ForeignKey("ticket_order.order_id", onupdate="CASCADE", ondelete="SET NULL"), nullable=True)

    concert = relationship("Concert", back_populates="tickets")
    sector = relationship("HallSector", back_populates="tickets")
```

### Модели схемы аудита и безопасности (схема audit из ЛР №3):

```python
# models/audit.py
from sqlalchemy import Column, Integer, Text, DateTime, LargeBinary
from database import Base

class MainLog(Base):
    __tablename__ = "main_log"
    __table_args__ = {"schema": "audit"}
    log_item_id = Column(Integer, primary_key=True, autoincrement=True)
    operation_type = Column(Text, nullable=False) # 'I', 'U', 'D'
    operation_date = Column(DateTime(timezone=True), nullable=False)
    user_operator = Column(Text, nullable=False)
    changed_data = Column(Text, nullable=False)

class SecretData(Base):
    __tablename__ = "secret_data"
    __table_args__ = {"schema": "audit"}
    ID = Column("ID", Integer, primary_key=True, autoincrement=True)
    username = Column(Text, nullable=False)
    secret_token = Column(LargeBinary, nullable=False)
```

---

## 4. Разграничение доступа и многопользовательский режим

В соответствии с результатами ЛР №3, в СУБД настроены 3 групповые роли и учетные записи:

1. **`ivan_customer` (роль `customer_group_role` — Зритель):**
   - Разрешенные объекты: представления `view_customer_afisha`, `view_customer_my_tickets`, таблица `concert`.
   - Запрещенные объекты: таблицы `artist`, `promoter`, `venue`, `hall_sector`, `ticket_order`, `audit.main_log`, `audit.secret_data`.
   - Права на запись: отсутствуют (только чтение).

2. **`petrov_staff` (роль `staff_group_role` — Персонал / Организатор):**
   - Разрешенные объекты: все таблицы схемы `public` (`artist`, `promoter`, `venue`, `hall_sector`, `customer`, `concert`, `ticket_order`, `ticket`) и служебные представления организатора (`view_promoter_sales_monitoring`, `view_promoter_gate_control`).
   - Запрещенные объекты: схема `audit` (`audit.main_log`, `audit.secret_data`).
   - Права на запись: разрешены `INSERT`, `UPDATE`, `DELETE` для таблиц мероприятий.

3. **`admin_user` (роль `admin_group_role` — Администратор):**
   - Полный доступ (ALL PRIVILEGES) ко всем таблицам и представлениям в схемах `public` и `audit`.
   - Доступ к просмотру логов безопасности и расшифровке секретных данных.

### Демонстрация работы ролевого доступа и перехвата исключений:

При попытке пользователя `ivan_customer` обратиться к закрытой таблице `artist` или схеме `audit` СУБД PostgreSQL возвращает ошибку отсутствия привилегий:

```text
psycopg2.errors.InsufficientPrivilege: ОШИБКА: нет доступа к таблице artist
```

Приложение перехватывает исключение `DBAPIError` и транслирует его в интерфейс пользователя с кодом состояния HTTP 403 Forbidden:

```python
try:
    db = get_session(user, pwd)
    rows = repo.get_all(db)
except DBAPIError as exc:
    return jsonify({
        "error": f"Ошибка СУБД PostgreSQL (psycopg2.errors.InsufficientPrivilege): {exc.orig}",
        "code": "DB_INSUFFICIENT_PRIVILEGE"
    }), 403
```

---

## 5. Демонстрация CRUD-операций через ORM

Взаимодействие с базой данных инкапсулировано в универсальном репозитории `BaseRepository`:

```python
# repositories/base.py
class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_all(self, session: Session, limit: int = 100, offset: int = 0, sort_by=None, sort_order="asc", filters=None):
        query = session.query(self.model)
        if sort_by and hasattr(self.model, sort_by):
            col = getattr(self.model, sort_by)
            query = query.order_by(desc(col) if sort_order == "desc" else asc(col))
        return query.offset(offset).limit(limit).all()

    def create(self, session: Session, obj_data: dict) -> ModelType:
        obj = self.model(**obj_data)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def delete(self, session: Session, id_value: any) -> bool:
        obj = session.get(self.model, id_value)
        if not obj:
            return False
        session.delete(obj)
        session.commit()
        return True
```

### Фиксация изменений в журнале аудита:
При выполнении операции `create` или `delete` от имени пользователя `petrov_staff` или `admin_user` автоматически срабатывает триггерная функция `public.logging()`, которая записывает событие в `audit.main_log`:

```json
{
  "log_item_id": 4,
  "operation_type": "I",
  "operation_date": "2026-11-05T22:30:00Z",
  "user_operator": "petrov_staff",
  "changed_data": "{\"concert_id\": 9, \"program_name\": \"Весенний тур 2026\", \"artist_id\": 1, \"venue_id\": 2, \"promoter_id\": 1}"
}
```

---

## 6. Сложные аналитические SQL-запросы с GROUP BY (п. 4 задания)

Для каждой группы пользователей разработан специализированный SQL-запрос, объединяющий более 2 сущностей и использующий группировку `GROUP BY`, с поддержкой интерактивной сортировки и фильтрации.

### 6.1. Запрос для роли Зрителя (`Customer`)
**Назначение:** Формирование сводки актуальной афиши с расчетом ценового диапазона и количества доступных к покупке билетов.  
**Сущности (4 шт.):** `concert`, `artist`, `venue`, `ticket`.  
**SQL-запрос:**
```sql
SELECT
    c.concert_id,
    c.program_name,
    c.start_datetime,
    c.age_restriction,
    a.stage_name AS artist,
    a.music_genre,
    v.venue_name,
    v.city,
    COUNT(t.ticket_id) AS available_tickets,
    COALESCE(MIN(t.price), 0) AS min_price,
    COALESCE(MAX(t.price), 0) AS max_price,
    ROUND(COALESCE(AVG(t.price), 0), 2) AS avg_price
FROM public.concert c
JOIN public.artist a ON c.artist_id = a.artist_id
JOIN public.venue v ON c.venue_id = v.venue_id
LEFT JOIN public.ticket t ON c.concert_id = t.concert_id AND t.ticket_status = 'Доступен'
WHERE (:city IS NULL OR v.city ILIKE :city)
  AND (:genre IS NULL OR a.music_genre ILIKE :genre)
GROUP BY c.concert_id, c.program_name, c.start_datetime, c.age_restriction,
         a.stage_name, a.music_genre, v.venue_name, v.city
HAVING (:max_price IS NULL OR COALESCE(MIN(t.price), 0) <= :max_price)
ORDER BY c.start_datetime ASC;
```

### 6.2. Запрос для роли Организатора (`Staff`)
**Назначение:** Мониторинг продаж билетов, процента заполняемости концертных площадок и совокупной выручки организаторов.  
**Сущности (5 шт.):** `concert`, `promoter`, `artist`, `venue`, `ticket`.  
**SQL-запрос:**
```sql
SELECT
    p.company_name AS promoter,
    c.concert_id,
    c.program_name,
    c.start_datetime,
    a.stage_name AS artist,
    v.venue_name,
    v.total_capacity,
    COUNT(CASE WHEN t.ticket_status = 'Продан' THEN 1 END) AS tickets_sold,
    ROUND(
        (COUNT(CASE WHEN t.ticket_status = 'Продан' THEN 1 END)::numeric /
        NULLIF(v.total_capacity, 0)) * 100,
        2
    ) AS occupancy_percent,
    COALESCE(SUM(CASE WHEN t.ticket_status = 'Продан' THEN t.price ELSE 0 END), 0) AS total_revenue,
    ROUND(AVG(CASE WHEN t.ticket_status = 'Продан' THEN t.price ELSE NULL END), 2) AS avg_sold_price
FROM public.concert c
JOIN public.promoter p ON c.promoter_id = p.promoter_id
JOIN public.artist a ON c.artist_id = a.artist_id
JOIN public.venue v ON c.venue_id = v.venue_id
LEFT JOIN public.ticket t ON c.concert_id = t.concert_id
WHERE (:promoter IS NULL OR p.company_name ILIKE :promoter)
GROUP BY p.company_name, c.concert_id, c.program_name, c.start_datetime,
         a.stage_name, v.venue_name, v.total_capacity
HAVING (:min_revenue IS NULL OR COALESCE(SUM(CASE WHEN t.ticket_status = 'Продан' THEN t.price ELSE 0 END), 0) >= :min_revenue)
ORDER BY total_revenue DESC;
```

### 6.3. Запрос для роли Администратора (`Admin`)
**Назначение:** Комплексный анализ коммерческой эффективности музыкальных исполнителей, охвата городов и средней доходности концертов.  
**Сущности (4 шт.):** `artist`, `concert`, `venue`, `ticket`.  
**SQL-запрос:**
```sql
SELECT
    a.artist_id,
    a.stage_name AS artist,
    a.music_genre,
    COUNT(DISTINCT c.concert_id) AS total_concerts,
    COUNT(DISTINCT v.city) AS cities_visited,
    COUNT(CASE WHEN t.ticket_status = 'Продан' THEN 1 END) AS total_tickets_sold,
    COALESCE(SUM(CASE WHEN t.ticket_status = 'Продан' THEN t.price ELSE 0 END), 0) AS total_gross,
    ROUND(
        COALESCE(SUM(CASE WHEN t.ticket_status = 'Продан' THEN t.price ELSE 0 END), 0) /
        NULLIF(COUNT(DISTINCT c.concert_id), 0),
        2
    ) AS avg_revenue_per_concert
FROM public.artist a
LEFT JOIN public.concert c ON a.artist_id = c.artist_id
LEFT JOIN public.venue v ON c.venue_id = v.venue_id
LEFT JOIN public.ticket t ON c.concert_id = t.concert_id
WHERE (:genre IS NULL OR a.music_genre ILIKE :genre)
GROUP BY a.artist_id, a.stage_name, a.music_genre
HAVING (:min_tickets IS NULL OR COUNT(CASE WHEN t.ticket_status = 'Продан' THEN 1 END) >= :min_tickets)
ORDER BY total_gross DESC;
```

---

## 7. Демонстрация криптографической защиты (pgcrypto)

В схеме `audit` хранится таблица `audit.secret_data`, содержащая симметрично зашифрованные токены доступа (AES-256). В веб-интерфейсе для роли Администратора реализована функция расшифровки через встроенную функцию `pgp_sym_decrypt`:

```sql
SELECT "ID", username, pgp_sym_decrypt(secret_token, '29aaa1424afb8e8c740fb247a9d44723c8b5c82d8a12994ee2ed8b64e4410b63') AS decrypted
FROM audit.secret_data
WHERE "ID" = 1;
```

Результат выполнения подтверждает успешное восстановление исходного значения токена (`token_admin_supersecret_access`).

---

## ВЫВОД

В ходе выполнения лабораторной работы №4 был успешно разработан прикладной уровень информационной системы «ConcertHub» на языке Python с использованием фреймворка Flask и ORM-системы SQLAlchemy 2.0.

Реализованы все поставленные задачи:
1. Выполнен полный объектно-реляционный маппинг сущностей, отношений и представлений, разработанных в ЛР №1–3.
2. Реализован веб-интерфейс с поддержкой многопользовательского доступа под учетными записями СУБД (`ivan_customer`, `petrov_staff`, `admin_user`, `postgres`).
3. Подтверждена работоспособность разграничения доступа на уровне СУБД с перехватом исключений `InsufficientPrivilege`.
4. Реализован динамический список доступных таблиц и CRUD-операции с регистрацией изменений триггерной системой логирования в `audit.main_log`.
5. Разработаны сложные агрегационные SQL-запросы с `GROUP BY` для каждой категории пользователей с фильтрацией и сортировкой данных.
6. Продемонстрирована работа расширения `pgcrypto` для защиты конфиденциальных данных.
