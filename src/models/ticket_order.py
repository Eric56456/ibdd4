"""
Модель заказа билетов (Ticket_Order) из ЛР №1 и №2.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from database import Base


class TicketOrder(Base):
    __tablename__ = "ticket_order"

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    order_datetime = Column(DateTime, default=datetime.utcnow, nullable=False)
    order_status = Column(Text, nullable=False) # 'Оплачен', 'Возврат'
    total_amount = Column(Numeric(10, 2), nullable=False)
    customer_id = Column(Integer, ForeignKey("customer.customer_id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)

    # Связи
    customer = relationship("Customer", back_populates="orders")
    tickets = relationship("Ticket", back_populates="order")

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "order_datetime": self.order_datetime.isoformat() if self.order_datetime else None,
            "order_status": self.order_status,
            "total_amount": float(self.total_amount) if self.total_amount is not None else 0.0,
            "customer_id": self.customer_id,
        }
