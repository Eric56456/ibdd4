"""
Модель организатора концертов (Promoter) из ЛР №1 и №2.
"""

from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import relationship
from database import Base


class Promoter(Base):
    __tablename__ = "promoter"

    promoter_id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(Text, nullable=False)
    contact_person = Column(Text, nullable=True)
    contact_phone = Column(Text, nullable=True)

    # Связь 1:M с концертами
    concerts = relationship("Concert", back_populates="promoter", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "promoter_id": self.promoter_id,
            "company_name": self.company_name,
            "contact_person": self.contact_person,
            "contact_phone": self.contact_phone,
        }
