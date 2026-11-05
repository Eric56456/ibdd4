"""
Модель сектора зрительного зала (Hall_Sector) из ЛР №1 и №2.
"""

from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class HallSector(Base):
    __tablename__ = "hall_sector"

    sector_id = Column(Integer, primary_key=True, autoincrement=True)
    sector_name = Column(Text, nullable=False)
    sector_capacity = Column(Integer, nullable=False)
    sector_type = Column(Text, nullable=True) # например 'танцевальный', 'сидячий'
    venue_id = Column(Integer, ForeignKey("venue.venue_id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)

    # Связи
    venue = relationship("Venue", back_populates="sectors")
    tickets = relationship("Ticket", back_populates="sector", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "sector_id": self.sector_id,
            "sector_name": self.sector_name,
            "sector_capacity": self.sector_capacity,
            "sector_type": self.sector_type,
            "venue_id": self.venue_id,
        }
