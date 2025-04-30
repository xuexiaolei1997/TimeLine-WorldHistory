from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

class EventBase(BaseModel):
    title: str
    description: str
    start_date: str
    end_date: str
    location: Dict
    zoom_level: int

class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    location: Optional[Dict] = None
    zoom_level: Optional[int] = None

class Event(EventBase):
    id: int

    class Config:
        orm_mode = True
