"""
Репозиторий сущности Venue (Концертные площадки).
"""

from models.venue import Venue
from repositories.base import BaseRepository


class VenueRepository(BaseRepository[Venue]):
    def __init__(self):
        super().__init__(Venue)


venue_repo = VenueRepository()
