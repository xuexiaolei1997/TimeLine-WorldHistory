from fastapi import Depends
from typing import Generator
from utils.database import db_manager
from services.event_service import EventService, EventRepository
from services.period_service import PeriodService, PeriodRepository
from services.region_service import RegionService, RegionRepository
from utils.cache import get_cache

def get_event_service(
    db = Depends(db_manager.get_db),
    cache = Depends(get_cache)
) -> EventService:
    """EventService dependency injection"""
    with db as database:
        repo = EventRepository(database)
        repo.cache = cache
        return EventService(repo)

def get_period_service(
    db = Depends(db_manager.get_db),
    cache = Depends(get_cache)
) -> PeriodService:
    """PeriodService dependency injection"""
    with db as database:
        repo = PeriodRepository(database)
        repo.cache = cache
        return PeriodService(repo)

def get_region_service(
    db = Depends(db_manager.get_db),
    cache = Depends(get_cache)
) -> RegionService:
    """RegionService dependency injection"""
    with db as database:
        repo = RegionRepository(database)
        repo.cache = cache
        return RegionService(repo)
