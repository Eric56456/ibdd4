"""
Репозиторий сущности Promoter (Организаторы).
"""

from models.promoter import Promoter
from repositories.base import BaseRepository


class PromoterRepository(BaseRepository[Promoter]):
    def __init__(self):
        super().__init__(Promoter)


promoter_repo = PromoterRepository()
