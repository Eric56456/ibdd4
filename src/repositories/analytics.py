"""
Репозиторий сложных аналитических запросов с GROUP BY (согласно заданию п. 4 ЛР №4).
Для каждой роли реализован запрос, объединяющий более 2 сущностей, с фильтрацией и сортировкой.
"""

from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session


class AnalyticsRepository:
    def get_customer_afisha_summary(
        self,
        session: Session,
        city: Optional[str] = None,
        genre: Optional[str] = None,
        max_price: Optional[float] = None,
        sort_by: str = "start_datetime",
        sort_order: str = "asc",
    ) -> List[dict]:
        """
        Сложный запрос для роли Зрителя (Customer).
        Объединяет сущности: Concert + Artist + Venue + Ticket (4 сущности).
        Группирует по концертам, площадкам и артистам, вычисляя диапазон цен и число доступных билетов.
        """
        valid_sort_cols = {
            "start_datetime": "c.start_datetime",
            "min_price": "min_price",
            "program_name": "c.program_name",
            "artist": "a.stage_name",
            "available_tickets": "available_tickets",
        }
        order_col = valid_sort_cols.get(sort_by, "c.start_datetime")
        direction = "DESC" if sort_order.lower() == "desc" else "ASC"

        sql = f"""
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
            ORDER BY {order_col} {direction}
        """

        params = {
            "city": f"%{city}%" if city else None,
            "genre": f"%{genre}%" if genre else None,
            "max_price": max_price if max_price is not None and max_price > 0 else None,
        }

        rows = session.execute(text(sql), params).fetchall()
        result = []
        for r in rows:
            result.append({
                "concert_id": r[0],
                "program_name": r[1],
                "start_datetime": r[2].isoformat() if r[2] else None,
                "age_restriction": r[3],
                "artist": r[4],
                "music_genre": r[5],
                "venue_name": r[6],
                "city": r[7],
                "available_tickets": r[8],
                "min_price": float(r[9]),
                "max_price": float(r[10]),
                "avg_price": float(r[11]),
            })
        return result

    def get_staff_sales_monitoring(
        self,
        session: Session,
        promoter: Optional[str] = None,
        min_revenue: Optional[float] = None,
        sort_by: str = "total_revenue",
        sort_order: str = "desc",
    ) -> List[dict]:
        """
        Сложный запрос для роли Персонала / Организатора (Staff).
        Объединяет сущности: Concert + Promoter + Artist + Venue + Ticket (5 сущностей).
        Группирует по промоутерам и концертам, рассчитывая доходы, процент заполняемости и средний чек.
        """
        valid_sort_cols = {
            "total_revenue": "total_revenue",
            "tickets_sold": "tickets_sold",
            "occupancy_percent": "occupancy_percent",
            "start_datetime": "c.start_datetime",
            "program_name": "c.program_name",
        }
        order_col = valid_sort_cols.get(sort_by, "total_revenue")
        direction = "DESC" if sort_order.lower() == "desc" else "ASC"

        sql = f"""
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
            ORDER BY {order_col} {direction}
        """

        params = {
            "promoter": f"%{promoter}%" if promoter else None,
            "min_revenue": min_revenue if min_revenue is not None and min_revenue > 0 else None,
        }

        rows = session.execute(text(sql), params).fetchall()
        result = []
        for r in rows:
            result.append({
                "promoter": r[0],
                "concert_id": r[1],
                "program_name": r[2],
                "start_datetime": r[3].isoformat() if r[3] else None,
                "artist": r[4],
                "venue_name": r[5],
                "total_capacity": r[6],
                "tickets_sold": r[7],
                "occupancy_percent": float(r[8]) if r[8] is not None else 0.0,
                "total_revenue": float(r[9]),
                "avg_sold_price": float(r[10]) if r[10] is not None else 0.0,
            })
        return result

    def get_admin_artist_stats(
        self,
        session: Session,
        genre: Optional[str] = None,
        min_tickets: Optional[int] = None,
        sort_by: str = "total_gross",
        sort_order: str = "desc",
    ) -> List[dict]:
        """
        Сложный запрос для роли Администратора (Admin).
        Объединяет сущности: Artist + Concert + Venue + Ticket (4 сущности).
        Группирует по исполнителям и музыкальным жанрам, вычисляя географию туров, суммарные сборы и средний доход.
        """
        valid_sort_cols = {
            "total_gross": "total_gross",
            "total_concerts": "total_concerts",
            "total_tickets_sold": "total_tickets_sold",
            "artist": "a.stage_name",
        }
        order_col = valid_sort_cols.get(sort_by, "total_gross")
        direction = "DESC" if sort_order.lower() == "desc" else "ASC"

        sql = f"""
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
            ORDER BY {order_col} {direction}
        """

        params = {
            "genre": f"%{genre}%" if genre else None,
            "min_tickets": min_tickets if min_tickets is not None and min_tickets > 0 else None,
        }

        rows = session.execute(text(sql), params).fetchall()
        result = []
        for r in rows:
            result.append({
                "artist_id": r[0],
                "artist": r[1],
                "music_genre": r[2],
                "total_concerts": r[3],
                "cities_visited": r[4],
                "total_tickets_sold": r[5],
                "total_gross": float(r[6]),
                "avg_revenue_per_concert": float(r[7]) if r[7] is not None else 0.0,
            })
        return result

    def get_admin_audit_activity(self, session: Session) -> List[dict]:
        """
        Аналитический отчет по активности операторов и типам операций в audit.main_log.
        Группировка по operation_type и user_operator с агрегацией счетчиков.
        """
        sql = """
            SELECT
                operation_type,
                user_operator,
                COUNT(*) AS operations_count,
                MIN(operation_date) AS first_operation,
                MAX(operation_date) AS last_operation
            FROM audit.main_log
            GROUP BY operation_type, user_operator
            ORDER BY operations_count DESC
        """
        rows = session.execute(text(sql)).fetchall()
        result = []
        for r in rows:
            result.append({
                "operation_type": r[0],
                "user_operator": r[1],
                "operations_count": r[2],
                "first_operation": r[3].isoformat() if r[3] else None,
                "last_operation": r[4].isoformat() if r[4] else None,
            })
        return result


analytics_repo = AnalyticsRepository()
