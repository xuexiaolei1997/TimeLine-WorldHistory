from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import IntEnum

class EventTitle(BaseModel):
    en: str = Field(..., min_length=1, max_length=100)
    zh: str = Field(..., min_length=1, max_length=100)
    
class EventDate(BaseModel):
    # 格式为yyyy-mm-dd
    start: str
    end: str

class EventLocation(BaseModel):
    """Geographic location coordinates"""
    coordinates: list[float]
    zoomLevel: int = Field(..., ge=1, le=20)  # Zoom level between 1 and 20

class EventMedia(BaseModel):
    images: list[str] = Field(..., min_items=0)
    videos: list[str] = Field(..., min_items=0)
    audios: list[str] = Field(..., min_items=0)

class EventDescription(BaseModel):
    en: str = Field(..., min_length=1)
    zh: str = Field(..., min_length=1)

class EventBase(BaseModel):
    """Base event model with validation"""
    title: EventTitle
    period: str
    region_id: Optional[str] = Field(None, description="Associated region ID")
    date: EventDate
    location: EventLocation
    description: EventDescription
    media: EventMedia

class EventCreate(EventBase):
    """Schema for creating new events"""
    pass

class EventUpdate(BaseModel):
    """Schema for updating events"""
    title: EventTitle
    period: str
    date: EventDate
    location: EventLocation
    description: EventDescription
    media: EventMedia

class Event(EventBase):
    """Complete event model with ID"""
    id: str = Field(..., alias="_id")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        allow_population_by_field_name = True
