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

@router.post("/create", response_model=Event)
@handle_app_exceptions
async def create_event(
    event: EventCreate, 
    repo: EventRepository = Depends(get_event_repo)
):
    """Create a new event"""
    logger.info(f"Creating new event: {event.title}")
    res = repo.create(event)
    return res

@router.post("/search", response_model=List[Event])
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

@router.get("/by-region/{region_id}", response_model=List[Event])
@cache_response(ttl=300)
@handle_app_exceptions
async def read_events_by_region(
    region_id: str,
    repo: EventRepository = Depends(get_event_repo)
):
    """Get events by region ID"""
    logger.info(f"Fetching events for region: {region_id}")
    return repo.get_by_region(region_id)

@router.post("/query", response_model=List[Event])
@cache_response(ttl=60)
@handle_app_exceptions
async def query_events(
    request: Request,
    start_date: Optional[str] = Query(None, regex=r"^\d{4}-\d{2}-\d{2}$"),
    end_date: Optional[str] = Query(None, regex=r"^\d{4}-\d{2}-\d{2}$"),
    region_id: Optional[str] = Query(None, description="Filter by region ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    repo: EventRepository = Depends(get_event_repo),
    **field_queries: Optional[str]
):
    """
    Flexible query events with:
    - Arbitrary field queries (fuzzy matching for strings)
    - Date range filtering (yyyy-mm-dd format)
    - Pagination
    
    Examples:
    - /query?title.en=war&period=ancient-rome
    - /query?date.start=2023-01-01&date.end=2023-12-31
    - /query?location.coordinates.0=116.4&location.coordinates.1=39.9
    """
    # Filter out None values and special params
    field_queries = {
        k: v for k, v in field_queries.items() 
        if v is not None and k not in ['skip', 'limit']
    }
    
    logger.info(f"Querying events with filters: {field_queries}, "
               f"start_date={start_date}, end_date={end_date}")
    
    return repo.query_events(
        field_queries=field_queries,
        start_date=start_date,
        end_date=end_date,
        region_id=region_id,
        skip=skip,
        limit=limit
    )

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
