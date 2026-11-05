"""
Модель концерта (Concert) из ЛР №1 и №2.
"""

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

    # Связи N:1
    artist = relationship("Artist", back_populates="concerts")
    venue = relationship("Venue", back_populates="concerts")
    promoter = relationship("Promoter", back_populates="concerts")

    # Связь 1:M с билетами
    tickets = relationship("Ticket", back_populates="concert", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "concert_id": self.concert_id,
            "program_name": self.program_name,
            "start_datetime": self.start_datetime.isoformat() if self.start_datetime else None,
            "age_restriction": self.age_restriction,
            "artist_id": self.artist_id,
            "venue_id": self.venue_id,
            "promoter_id": self.promoter_id,
        }
