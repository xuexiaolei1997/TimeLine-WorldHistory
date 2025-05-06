from fastapi import APIRouter, Depends, Query, Request
from typing import List, Optional
import logging
from fastapi.logger import logger
from utils.cache import cache_response

from services.event_service import EventRepository
from schemas.event_schemas import EventCreate, Event, EventUpdate
from utils.database import get_db
from utils.decorators import handle_app_exceptions
router = APIRouter(prefix="/events", tags=["events"])

def get_event_repo(
    request: Request,
    db = Depends(get_db)
) -> EventRepository:
    """Dependency for getting EventRepository instance"""
    with db as database:
        repo = EventRepository(database)
        repo.cache = request.app.state.cache
        return repo

@router.post("/", response_model=Event)
@handle_app_exceptions
async def create_event(
    event: EventCreate, 
    repo: EventRepository = Depends(get_event_repo)
):
    """Create a new event"""
    logger.info(f"Creating new event: {event.title}")
    res = repo.create(event)
    return res

@router.get("/", response_model=List[Event])
@cache_response(ttl=60)
async def read_events(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    repo: EventRepository = Depends(get_event_repo)
):
    """Get list of events with pagination"""
    logger.info(f"Fetching events (skip={skip}, limit={limit})")
    res = repo.list(skip=skip, limit=limit)
    return res

@router.get("/search", response_model=List[Event])
@cache_response(ttl=60)
async def search_events(
    request: Request,
    query: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    repo: EventRepository = Depends(get_event_repo)
):
    """Search events by title or description"""
    logger.info(f"Searching events for: {query}")
    res = repo.search(query, skip=skip, limit=limit)
    return res

@router.get("/by-title/{title}", response_model=Optional[Event])
@cache_response(ttl=300)
@handle_app_exceptions
async def read_event_by_title(
    title: str,
    repo: EventRepository = Depends(get_event_repo)
):
    """Get event by exact title match"""
    logger.info(f"Fetching event by title: {title}")
    return repo.get_by_title(title)

@router.get("/{event_id}", response_model=Event)
@handle_app_exceptions
async def read_event(
    event_id: str,
    repo: EventRepository = Depends(get_event_repo)
):
    """Get event by ID"""
    logger.info(f"Fetching event by ID: {event_id}")
    ret = repo.get(event_id)
    return ret

@router.put("/{event_id}", response_model=Event)
@handle_app_exceptions
async def update_event(
    event_id: str,
    event: EventUpdate,
    repo: EventRepository = Depends(get_event_repo)
):
    """Update an existing event"""
    logger.info(f"Updating event {event_id}")
    res = repo.update(event_id, event)
    return res

@router.delete("/{event_id}")
@handle_app_exceptions
async def delete_event(
    event_id: str,
    repo: EventRepository = Depends(get_event_repo)
):
    """Delete an event"""
    logger.info(f"Deleting event {event_id}")
    repo.delete(event_id)
    return {"message": "Event deleted successfully"}
