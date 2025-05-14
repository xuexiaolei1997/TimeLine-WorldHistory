from fastapi import APIRouter, Depends, Query, Request
from typing import List, Optional
import logging
from fastapi.logger import logger
from utils.cache import cache_response

from services.event_service import EventRepository, get_event_repo
from schemas.event_schemas import EventCreate, Event, EventUpdate
from utils.decorators import handle_app_exceptions, wrap_response
from datetime import datetime

router = APIRouter(prefix="/events", tags=["events"])

def transform_event(event: dict) -> dict:
    """Transform event for frontend compatibility"""
    return {
        "id": str(event["_id"]),
        "title": event["title"],
        "date": event["date"],
        "location": event["location"],
        "content": event.get("content", {}),
        "media": event.get("media", {})
    }

@router.get("/", response_model=dict)
@cache_response(ttl=300)
@handle_app_exceptions
async def list_events(
    repo: EventRepository = Depends(get_event_repo)
):
    """Get all events in frontend-compatible format"""
    logger.info("Fetching all events")
    events = repo.query_events()
    transformed = [transform_event(event) for event in events]
    return wrap_response(data=transformed)

@router.post("/create", response_model=dict)
@handle_app_exceptions
async def create_event(
    event: EventCreate, 
    repo: EventRepository = Depends(get_event_repo)
):
    """Create a new event"""
    logger.info(f"Creating new event: {event.title}")
    result = repo.create(event.dict())
    return wrap_response(data=transform_event(result))

@router.get("/search", response_model=dict)
@cache_response(ttl=60)
@handle_app_exceptions
async def search_events(
    query: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    repo: EventRepository = Depends(get_event_repo)
):
    """Search events by title or description"""
    logger.info(f"Searching events with query: {query}")
    events = repo.search(query, skip=skip, limit=limit)
    return wrap_response(data=[transform_event(event) for event in events])

@router.get("/by-title/{title}", response_model=dict)
@cache_response(ttl=300)
@handle_app_exceptions
async def read_event_by_title(
    title: str,
    repo: EventRepository = Depends(get_event_repo)
):
    """Get event by exact title match"""
    logger.info(f"Fetching event by title: {title}")
    event = repo.get_by_title(title)
    return wrap_response(data=transform_event(event) if event else None)

@router.get("/by-region/{region_id}", response_model=dict)
@cache_response(ttl=300)
@handle_app_exceptions
async def read_events_by_region(
    region_id: str,
    repo: EventRepository = Depends(get_event_repo)
):
    """Get events by region ID"""
    logger.info(f"Fetching events for region: {region_id}")
    events = repo.get_by_region(region_id)
    return wrap_response(data=[transform_event(event) for event in events])

@router.get("/{event_id}", response_model=dict)
@handle_app_exceptions
async def read_event(
    event_id: str,
    repo: EventRepository = Depends(get_event_repo)
):
    """Get event by ID"""
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
    """Update an existing event"""
    logger.info(f"Updating event {event_id}")
    result = repo.update(event_id, event.dict(exclude_unset=True))
    return wrap_response(data=transform_event(result))

@router.delete("/{event_id}", response_model=dict)
@handle_app_exceptions
async def delete_event(
    event_id: str,
    repo: EventRepository = Depends(get_event_repo)
):
    """Delete an event"""
    logger.info(f"Deleting event {event_id}")
    repo.delete(event_id)
    return wrap_response(data={"message": "Event deleted successfully"})
