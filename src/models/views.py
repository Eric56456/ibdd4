"""
Модели представлений (Views) из ЛР №2 для ORM-маппинга.
"""

from sqlalchemy import Column, Integer, Text, DateTime, Numeric
from database import Base


class ViewCustomerAfisha(Base):
    """Представление 1: Публичная афиша для зрителей."""
    __tablename__ = "view_customer_afisha"

    concert_id = Column(Integer, primary_key=True)
    artist = Column(Text)
    program_name = Column(Text)
    start_datetime = Column(DateTime)
    age_restriction = Column(Text)
    city = Column(Text)
    venue_name = Column(Text)
    price_from = Column(Numeric(10, 2))

    def to_dict(self):
        return {
            "concert_id": self.concert_id,
            "artist": self.artist,
            "program_name": self.program_name,
            "start_datetime": self.start_datetime.isoformat() if self.start_datetime else None,
            "age_restriction": self.age_restriction,
            "city": self.city,
            "venue_name": self.venue_name,
            "price_from": float(self.price_from) if self.price_from is not None else None,
        }


class ViewCustomerMyTickets(Base):
    """Представление 2: Мои купленные билеты."""
    __tablename__ = "view_customer_my_tickets"

    barcode = Column(Text, primary_key=True)
    customer_id = Column(Integer)
    customer_full_name = Column(Text)
    artist = Column(Text)
    program_name = Column(Text)
    start_datetime = Column(DateTime)
    venue_name = Column(Text)
    sector_name = Column(Text)
    price = Column(Numeric(10, 2))

    def to_dict(self):
        return {
            "barcode": self.barcode,
            "customer_id": self.customer_id,
            "customer_full_name": self.customer_full_name,
            "artist": self.artist,
            "program_name": self.program_name,
            "start_datetime": self.start_datetime.isoformat() if self.start_datetime else None,
            "venue_name": self.venue_name,
            "sector_name": self.sector_name,
            "price": float(self.price) if self.price is not None else None,
        }


class ViewPromoterSalesMonitoring(Base):
    """Представление 3: Мониторинг продаж для организатора."""
    __tablename__ = "view_promoter_sales_monitoring"

    program_name = Column(Text, primary_key=True)
    promoter = Column(Text)
    artist = Column(Text)
    venue_name = Column(Text)
    total_capacity = Column(Integer)
    tickets_sold = Column(Integer)
    occupancy_percent = Column(Numeric(5, 2))
    total_revenue = Column(Numeric(12, 2))

    def to_dict(self):
        return {
            "promoter": self.promoter,
            "artist": self.artist,
            "program_name": self.program_name,
            "venue_name": self.venue_name,
            "total_capacity": self.total_capacity,
            "tickets_sold": self.tickets_sold,
            "occupancy_percent": float(self.occupancy_percent) if self.occupancy_percent is not None else 0.0,
            "total_revenue": float(self.total_revenue) if self.total_revenue is not None else 0.0,
        }


class ViewPromoterGateControl(Base):
    """Представление 4: Контроль на входе (Gate-control)."""
    __tablename__ = "view_promoter_gate_control"

    barcode = Column(Text, primary_key=True)
    concert_id = Column(Integer)
    start_datetime = Column(DateTime)
    ticket_status = Column(Text)
    sector_name = Column(Text)
    sector_type = Column(Text)
    customer_full_name = Column(Text)
    phone_number = Column(Text)

    def to_dict(self):
        return {
            "barcode": self.barcode,
            "concert_id": self.concert_id,
            "start_datetime": self.start_datetime.isoformat() if self.start_datetime else None,
            "ticket_status": self.ticket_status,
            "sector_name": self.sector_name,
            "sector_type": self.sector_type,
            "customer_full_name": self.customer_full_name,
            "phone_number": self.phone_number,
        }


class ViewArtistPopularity(Base):
    """Представление 5: Популярность артистов (статистика)."""
    __tablename__ = "view_artist_popularity"

    artist = Column(Text, primary_key=True)
    music_genre = Column(Text)
    total_concerts = Column(Integer)
    cities_visited = Column(Integer)
    total_tickets_sold = Column(Integer)
    total_gross = Column(Numeric(12, 2))

    def to_dict(self):
        return {
            "artist": self.artist,
            "music_genre": self.music_genre,
            "total_concerts": self.total_concerts,
            "cities_visited": self.cities_visited,
            "total_tickets_sold": self.total_tickets_sold,
            "total_gross": float(self.total_gross) if self.total_gross is not None else 0.0,
        }
