"""
Модель исполнителя (Artist) из ЛР №1 и №2.
"""

from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import relationship
from database import Base


class Artist(Base):
    __tablename__ = "artist"

    artist_id = Column(Integer, primary_key=True, autoincrement=True)
    stage_name = Column(Text, nullable=False)
    leader_full_name = Column(Text, nullable=True)
    music_genre = Column(Text, nullable=True)

    # Связь 1:M с концертами
    concerts = relationship("Concert", back_populates="artist", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "artist_id": self.artist_id,
            "stage_name": self.stage_name,
            "leader_full_name": self.leader_full_name,
            "music_genre": self.music_genre,
        }
