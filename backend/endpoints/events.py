from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from services.event_service import EventRepository
from schemas.event_schemas import EventCreate, Event, EventUpdate
from utils.database import db_manager
from utils.decorators import handle_app_exceptions

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=Event)
@handle_app_exceptions
def create_event(event: EventCreate, db: Session = Depends(db_manager.get_db)):
    repo = EventRepository(db)
    return repo.create(event.dict())

@router.get("/", response_model=List[Event])
def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(db_manager.get_db)):
    repo = EventRepository(db)
    return repo.list(skip=skip, limit=limit)

@router.get("/{event_id}", response_model=Event)
@handle_app_exceptions
def read_event(event_id: int, db: Session = Depends(db_manager.get_db)):
    repo = EventRepository(db)
    return repo.get(event_id)

@router.put("/{event_id}", response_model=Event)
@handle_app_exceptions
def update_event(event_id: int, event: EventUpdate, db: Session = Depends(db_manager.get_db)):
    repo = EventRepository(db)
    return repo.update(event_id, event.dict(exclude_unset=True))

@router.delete("/{event_id}")
@handle_app_exceptions
def delete_event(event_id: int, db: Session = Depends(db_manager.get_db)):
    repo = EventRepository(db)
    repo.delete(event_id)
    return {"message": "Event deleted successfully"}
