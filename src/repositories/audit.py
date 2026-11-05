"""
Репозиторий аудита и секретных данных (схема audit из ЛР №3).
"""

from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from models.audit import MainLog, SecretData
from repositories.base import BaseRepository


class AuditRepository(BaseRepository[MainLog]):
    def __init__(self):
        super().__init__(MainLog)

    def get_logs(self, session: Session, limit: int = 50) -> List[dict]:
        """Получает последние записи из журнала аудита."""
        logs = session.query(MainLog).order_by(MainLog.log_item_id.desc()).limit(limit).all()
        return [l.to_dict() for l in logs]

    def get_secrets(self, session: Session) -> List[dict]:
        """Получает зашифрованные токены (доступно только роли администратора)."""
        secrets = session.query(SecretData).all()
        return [s.to_dict() for s in secrets]

    def decrypt_secret(self, session: Session, record_id: int, key: str) -> Optional[dict]:
        """Демонстрация расшифровки pgp_sym_decrypt в соответствии с ЛР №3."""
        sql = text("""
            SELECT "ID", username, pgp_sym_decrypt(secret_token, :key) as decrypted
            FROM audit.secret_data
            WHERE "ID" = :id
        """)
        row = session.execute(sql, {"id": record_id, "key": key}).fetchone()
        if row:
            return {
                "ID": row[0],
                "username": row[1],
                "decrypted_token": row[2],
            }
        return None


audit_repo = AuditRepository()
