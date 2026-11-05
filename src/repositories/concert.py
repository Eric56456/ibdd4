"""
Репозиторий сущности Concert (Концерты).
"""

from models.concert import Concert
from repositories.base import BaseRepository


class ConcertRepository(BaseRepository[Concert]):
    def __init__(self):
        super().__init__(Concert)


concert_repo = ConcertRepository()
