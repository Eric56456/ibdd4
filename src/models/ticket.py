"""
Модель билета (Ticket) из ЛР №1 и №2.
"""

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

    # Связи N:1
    concert = relationship("Concert", back_populates="tickets")
    sector = relationship("HallSector", back_populates="tickets")
    order = relationship("TicketOrder", back_populates="tickets")

    def to_dict(self):
        return {
            "ticket_id": self.ticket_id,
            "barcode": self.barcode,
            "price": float(self.price) if self.price is not None else 0.0,
            "ticket_status": self.ticket_status,
            "concert_id": self.concert_id,
            "sector_id": self.sector_id,
            "order_id": self.order_id,
        }
