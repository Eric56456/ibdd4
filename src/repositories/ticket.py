"""
Репозиторий сущности Ticket (Билеты).
"""

from models.ticket import Ticket
from repositories.base import BaseRepository


class TicketRepository(BaseRepository[Ticket]):
    def __init__(self):
        super().__init__(Ticket)


ticket_repo = TicketRepository()
