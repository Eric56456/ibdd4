"""
Модели изолированной схемы audit (audit.main_log и audit.secret_data) из ЛР №3.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, LargeBinary
from database import Base


class MainLog(Base):
    __tablename__ = "main_log"
    __table_args__ = {"schema": "audit"}

    log_item_id = Column(Integer, primary_key=True, autoincrement=True)
    operation_type = Column(Text, nullable=False) # 'I', 'U', 'D'
    operation_date = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    user_operator = Column(Text, nullable=False)
    changed_data = Column(Text, nullable=False)

    def to_dict(self):
        return {
            "log_item_id": self.log_item_id,
            "operation_type": self.operation_type,
            "operation_date": self.operation_date.isoformat() if self.operation_date else None,
            "user_operator": self.user_operator,
            "changed_data": self.changed_data,
        }


class SecretData(Base):
    __tablename__ = "secret_data"
    __table_args__ = {"schema": "audit"}

    ID = Column("ID", Integer, primary_key=True, autoincrement=True)
    username = Column(Text, nullable=False)
    secret_token = Column(LargeBinary, nullable=False)

    def to_dict(self):
        return {
            "ID": self.ID,
            "username": self.username,
            "secret_token": f"\\x{self.secret_token.hex()}" if isinstance(self.secret_token, (bytes, bytearray)) else str(self.secret_token),
        }
