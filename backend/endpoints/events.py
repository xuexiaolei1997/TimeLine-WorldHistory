from fastapi import APIRouter, Depends, Query, Request
from typing import List, Optional
from fastapi.logger import logger
from utils.cache import cache_response
from utils.decorators import handle_app_exceptions, wrap_response
from datetime import datetime

from services.event_service import EventRepository, EventService
from utils.database import db_manager
from schemas.event_schemas import EventCreate, EventUpdate, Event, EventPeriod

router = APIRouter(prefix="/events", tags=["events"])

def get_event_service(
    request: Request,
    db = Depends(db_manager.get_db())
) -> EventService:
    """Dependency for getting EventService instance"""
    with db as database:
        repo = EventRepository(database)
        repo.cache = request.app.state.cache
        return EventService(repo)

def transform_event(event: dict) -> dict:
    """Transform event for frontend compatibility with enhanced error handling"""
    if not event:
        return None
    
    try:
        # 确保基础字段存在且有默认值
        base_event = {
            "id": str(event.get("_id", "")) or event.get("id", ""),
            "title": {
                "en": "",
                "zh": ""
            },
            "period": "modern",  # 默认值
            "date": {
                "start": None,
                "end": None
            },
            "location": {
                "coordinates": [0, 0],
                "zoomLevel": 1,
                "highlightColor": "#FF0000",
                "region_name": None
            },
            "description": {
                "en": "",
                "zh": ""
            },
            "media": {
                "images": [],
                "videos": [],
                "audios": [],
                "thumbnail": None
            },
            "contentRefs": {
                "articles": [],
                "images": [],
                "videos": [],
                "documents": []
            },
            "tags": {
                "category": [],
                "keywords": []
            },
            "importance": 1,
            "is_public": True,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }

        # 更新存在的字段
        if isinstance(event.get("title"), dict):
            base_event["title"].update(event["title"])
        elif isinstance(event.get("title"), str):
            base_event["title"]["en"] = event["title"]
            
        if event.get("period"):
            base_event["period"] = event["period"]
            
        if isinstance(event.get("date"), dict):
            base_event["date"].update(event["date"])
            
        if isinstance(event.get("location"), dict):
            base_event["location"].update(event["location"])
            
        if isinstance(event.get("description"), dict):
            base_event["description"].update(event["description"])
            
        if isinstance(event.get("media"), dict):
            base_event["media"].update(event["media"])
            
        if isinstance(event.get("contentRefs"), dict):
            base_event["contentRefs"].update(event["contentRefs"])
            
        if isinstance(event.get("tags"), dict):
            base_event["tags"].update(event["tags"])
            
        if event.get("importance"):
            base_event["importance"] = int(event["importance"])
            
        if event.get("is_public") is not None:
            base_event["is_public"] = bool(event["is_public"])
            
        # 处理时间戳
        for field in ["created_at", "last_updated"]:
            if event.get(field):
                try:
                    if isinstance(event[field], datetime):
                        base_event[field] = event[field].isoformat()
                    else:
                        base_event[field] = event[field]
                except Exception:
                    pass  # 保持默认值
                    
        return base_event
        
    except Exception as e:
        logger.error(f"Error transforming event: {str(e)}")
        # 返回基本数据结构而不是None，避免422错误
        return {
            "id": str(event.get("_id", "")) if event.get("_id") else "",
            "title": {"en": "", "zh": ""},
            "period": "modern",
            "date": {"start": None, "end": None},
            "location": {"coordinates": [0, 0], "zoomLevel": 1},
            "description": {"en": "", "zh": ""},
            "importance": 1,
            "is_public": True,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
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
    service: EventService = Depends(get_event_service)
):
    """Get events list with advanced filtering and sorting"""
    logger.info(f"Fetching events with filters: query={query}, period={period}")
    events = service.search_events(
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
    service: EventService = Depends(get_event_service)
):
    """Create new event"""
    logger.info(f"Creating new event: {event.title}")
    result = service.create(event)
    return wrap_response(data=transform_event(result))

@router.get("/{event_id}", response_model=dict)
@cache_response(ttl=300)
@handle_app_exceptions
async def get_event(
    event_id: str,
    service: EventService = Depends(get_event_service)
):
    """Get event by ID"""
    logger.info(f"Fetching event by ID: {event_id}")
    event = service.get(event_id)
    return wrap_response(data=transform_event(event))

@router.put("/{event_id}", response_model=dict)
@handle_app_exceptions
async def update_event(
    event_id: str,
    event: EventUpdate,
    service: EventService = Depends(get_event_service)
):
    """Update event"""
    logger.info(f"Updating event {event_id}")
    result = service.update(event_id, event)
    return wrap_response(data=transform_event(result))

@router.delete("/{event_id}", response_model=dict)
@handle_app_exceptions
async def delete_event(
    event_id: str,
    service: EventService = Depends(get_event_service)
):
    """Delete event"""
    logger.info(f"Deleting event {event_id}")
    service.delete(event_id)
    return wrap_response(data={"message": "Event deleted successfully"})

@router.get("/by-period/{period}", response_model=dict)
@cache_response(ttl=300)
@handle_app_exceptions
async def get_events_by_period(
    period: EventPeriod,
    service: EventService = Depends(get_event_service)
):
    """Get all events for specific period"""
    logger.info(f"Fetching events for period: {period}")
    events = service.get_by_period(period.value)
    return wrap_response(data=[transform_event(event) for event in events])

@router.get("/by-region/{region_name}", response_model=dict)
@cache_response(ttl=300)
@handle_app_exceptions
async def get_events_by_region(
    region_name: str,
    service: EventService = Depends(get_event_service)
):
    """Get all events for specific region"""
    logger.info(f"Fetching events for region: {region_name}")
    events = service.get_by_region(region_name)
    return wrap_response(data=[transform_event(event) for event in events])
