"""
Модель зрителя (Customer) из ЛР №1 и №2 с полем birth_date.
"""

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

    # Связь 1:M с заказами
    orders = relationship("TicketOrder", back_populates="customer", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "customer_full_name": self.customer_full_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
        }
