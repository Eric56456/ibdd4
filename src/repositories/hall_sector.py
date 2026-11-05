"""
Репозиторий сущности HallSector (Секторы зала).
"""

from models.hall_sector import HallSector
from repositories.base import BaseRepository


class HallSectorRepository(BaseRepository[HallSector]):
    def __init__(self):
        super().__init__(HallSector)


hall_sector_repo = HallSectorRepository()
