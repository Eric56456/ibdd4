"""
Репозиторий сущности TicketOrder (Заказы билетов).
"""

from models.ticket_order import TicketOrder
from repositories.base import BaseRepository


class TicketOrderRepository(BaseRepository[TicketOrder]):
    def __init__(self):
        super().__init__(TicketOrder)


ticket_order_repo = TicketOrderRepository()
