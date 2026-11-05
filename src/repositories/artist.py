"""
Репозиторий сущности Artist (Исполнители).
"""

from models.artist import Artist
from repositories.base import BaseRepository


class ArtistRepository(BaseRepository[Artist]):
    def __init__(self):
        super().__init__(Artist)


artist_repo = ArtistRepository()
