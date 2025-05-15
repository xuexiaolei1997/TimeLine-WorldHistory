from fastapi import APIRouter, Depends, Query, Request
from typing import List, Optional
from fastapi.logger import logger
from utils.cache import cache_response
from utils.decorators import handle_app_exceptions, wrap_response
from datetime import datetime

from services.event_service import EventRepository
from utils.database import get_db
from schemas.event_schemas import EventCreate, EventUpdate, Event, EventPeriod

router = APIRouter(prefix="/events", tags=["events"])

def get_event_repo(
    request: Request,
    db = Depends(get_db)
) -> EventRepository:
    """Dependency for getting PeriodRepository instance"""
    with db as database:
        repo = EventRepository(database)
        repo.cache = request.app.state.cache
        return repo

def transform_event(event: dict) -> dict:
    """Transform event for frontend compatibility"""
    if not event:
        return None
    
    return {
        "id": event.get("id") or str(event.get("_id")),
        "title": event["title"],
        "period": event["period"],
        "date": event["date"],
        "location": event["location"],
        "description": event["description"],
        "media": event.get("media", {}),
        "contentRefs": event.get("contentRefs", {
            "articles": [],
            "images": [],
            "videos": [],
            "documents": []
        }),
        "tags": event.get("tags", {
            "category": [],
            "keywords": []
        }),
        "importance": event.get("importance", 1),
        "is_public": event.get("is_public", True),
        "created_at": event.get("created_at", datetime.now()).isoformat(),
        "last_updated": event.get("last_updated", datetime.now()).isoformat()
    }

@router.get("/", response_model=dict)
@cache_response(ttl=300)
@handle_app_exceptions
async def list_events(
    query: Optional[str] = None,
    period: Optional[EventPeriod] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    importance_min: Optional[int] = Query(None, ge=1, le=5),
    is_public: Optional[bool] = None,
    region_name: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    sort_by: Optional[str] = None,
    sort_order: int = Query(1, ge=-1, le=1),
    repo: EventRepository = Depends(get_event_repo)
):
    """获取事件列表，支持高级筛选和排序"""
    logger.info(f"Fetching events with filters: query={query}, period={period}")
    events = repo.search_events(
        query=query,
        period=period.value if period else None,
        start_date=start_date,
        end_date=end_date,
        tags=tags,
        importance_min=importance_min,
        is_public=is_public,
        region_name=region_name,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    transformed = [transform_event(event) for event in events]
    return wrap_response(data=transformed)

@router.post("/", response_model=dict)
@handle_app_exceptions
async def create_event(
    event: EventCreate,
    repo: EventRepository = Depends(get_event_repo)
):
    """创建新事件"""
    logger.info(f"Creating new event: {event.title}")
    result = repo.create(event)
    return wrap_response(data=transform_event(result))

@router.get("/{event_id}", response_model=dict)
@cache_response(ttl=300)
@handle_app_exceptions
async def get_event(
    event_id: str,
    repo: EventRepository = Depends(get_event_repo)
):
    """根据ID获取事件"""
    logger.info(f"Fetching event by ID: {event_id}")
    event = repo.get(event_id)
    return wrap_response(data=transform_event(event))

@router.put("/{event_id}", response_model=dict)
@handle_app_exceptions
async def update_event(
    event_id: str,
    event: EventUpdate,
    repo: EventRepository = Depends(get_event_repo)
):
    """更新事件"""
    logger.info(f"Updating event {event_id}")
    result = repo.update(event_id, event)
    return wrap_response(data=transform_event(result))

@router.delete("/{event_id}", response_model=dict)
@handle_app_exceptions
async def delete_event(
    event_id: str,
    repo: EventRepository = Depends(get_event_repo)
):
    """删除事件"""
    logger.info(f"Deleting event {event_id}")
    repo.delete(event_id)
    return wrap_response(data={"message": "Event deleted successfully"})

@router.get("/by-period/{period}", response_model=dict)
@cache_response(ttl=300)
@handle_app_exceptions
async def get_events_by_period(
    period: EventPeriod,
    repo: EventRepository = Depends(get_event_repo)
):
    """获取特定时期的所有事件"""
    logger.info(f"Fetching events for period: {period}")
    events = repo.get_by_period(period.value)
    return wrap_response(data=[transform_event(event) for event in events])

@router.get("/by-region/{region_name}", response_model=dict)
@cache_response(ttl=300)
@handle_app_exceptions
async def get_events_by_region(
    region_name: str,
    repo: EventRepository = Depends(get_event_repo)
):
    """获取特定区域的所有事件"""
    logger.info(f"Fetching events for region: {region_name}")
    events = repo.get_by_region(region_name)
    return wrap_response(data=[transform_event(event) for event in events])
