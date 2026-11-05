"""
Репозиторий сущности Customer (Зрители).
"""

from models.customer import Customer
from repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self):
        super().__init__(Customer)


customer_repo = CustomerRepository()
