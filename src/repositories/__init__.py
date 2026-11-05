"""
Пакет репозиториев для взаимодействия с базой данных ConcertHub.
"""

from repositories.base import BaseRepository
from repositories.artist import artist_repo, ArtistRepository
from repositories.promoter import promoter_repo, PromoterRepository
from repositories.venue import venue_repo, VenueRepository
from repositories.hall_sector import hall_sector_repo, HallSectorRepository
from repositories.customer import customer_repo, CustomerRepository
from repositories.concert import concert_repo, ConcertRepository
from repositories.ticket_order import ticket_order_repo, TicketOrderRepository
from repositories.ticket import ticket_repo, TicketRepository
from repositories.audit import audit_repo, AuditRepository
from repositories.analytics import analytics_repo, AnalyticsRepository

# Справочник репозиториев по именам сущностей
REPOSITORIES_MAP = {
    "artist": artist_repo,
    "promoter": promoter_repo,
    "venue": venue_repo,
    "hall_sector": hall_sector_repo,
    "customer": customer_repo,
    "concert": concert_repo,
    "ticket_order": ticket_order_repo,
    "ticket": ticket_repo,
    "main_log": audit_repo,
}

__all__ = [
    "BaseRepository",
    "artist_repo",
    "promoter_repo",
    "venue_repo",
    "hall_sector_repo",
    "customer_repo",
    "concert_repo",
    "ticket_order_repo",
    "ticket_repo",
    "audit_repo",
    "analytics_repo",
    "REPOSITORIES_MAP",
]
