"""
Модель концертной площадки (Venue) из ЛР №1 и №2.
"""

from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import relationship
from database import Base


class Venue(Base):
    __tablename__ = "venue"

    venue_id = Column(Integer, primary_key=True, autoincrement=True)
    venue_name = Column(Text, nullable=False)
    city = Column(Text, nullable=False)
    address = Column(Text, nullable=True)
    total_capacity = Column(Integer, nullable=True)

    # Связи 1:M
    sectors = relationship("HallSector", back_populates="venue", cascade="all, delete-orphan")
    concerts = relationship("Concert", back_populates="venue", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "venue_id": self.venue_id,
            "venue_name": self.venue_name,
            "city": self.city,
            "address": self.address,
            "total_capacity": self.total_capacity,
        }
