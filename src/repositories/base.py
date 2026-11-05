"""
Базовый класс репозитория с обобщенными CRUD-операциями через SQLAlchemy ORM.
"""

from typing import Generic, List, Optional, Type, TypeVar
from sqlalchemy import desc, asc
from sqlalchemy.orm import Session
from database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_all(
        self,
        session: Session,
        limit: int = 100,
        offset: int = 0,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        filters: Optional[dict] = None,
    ) -> List[ModelType]:
        """Получение списка записей с поддержкой фильтрации, сортировки и пагинации."""
        query = session.query(self.model)

        # Применение строковой фильтрации по полям
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None and value != "":
                    column = getattr(self.model, field)
                    if isinstance(value, str):
                        query = query.filter(column.ilike(f"%{value}%"))
                    else:
                        query = query.filter(column == value)

        # Применение сортировки
        if sort_by and hasattr(self.model, sort_by):
            col = getattr(self.model, sort_by)
            query = query.order_by(desc(col) if sort_order == "desc" else asc(col))

        return query.offset(offset).limit(limit).all()

    def get_by_id(self, session: Session, id_value: any) -> Optional[ModelType]:
        """Получение одной записи по первичному ключу."""
        return session.get(self.model, id_value)

    def create(self, session: Session, obj_data: dict) -> ModelType:
        """Вставка новой записи с фиксацией транзакции."""
        # Фильтруем данные по существующим колонкам модели
        valid_cols = {c.name for c in self.model.__table__.columns}
        filtered_data = {k: v for k, v in obj_data.items() if k in valid_cols and v != ""}
        obj = self.model(**filtered_data)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    def update(self, session: Session, id_value: any, obj_data: dict) -> Optional[ModelType]:
        """Обновление существующей записи по первичному ключу."""
        obj = self.get_by_id(session, id_value)
        if not obj:
            return None
        valid_cols = {c.name for c in self.model.__table__.columns}
        for k, v in obj_data.items():
            if k in valid_cols and hasattr(obj, k):
                setattr(obj, k, v if v != "" else None)
        session.commit()
        session.refresh(obj)
        return obj

    def delete(self, session: Session, id_value: any) -> bool:
        """Удаление записи по первичному ключу."""
        obj = self.get_by_id(session, id_value)
        if not obj:
            return False
        session.delete(obj)
        session.commit()
        return True
