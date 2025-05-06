from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import IntEnum

class Location(BaseModel):
    """Geographic location coordinates"""
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    name: Optional[str] = None

class ZoomLevel(IntEnum):
    """Zoom level enum for map display"""
    CONTINENT = 1
    COUNTRY = 5
    CITY = 10
    STREET = 15
    BUILDING = 20

class EventBase(BaseModel):
    """Base event model with validation"""
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    start_date: datetime
    end_date: datetime
    location: Location
    zoom_level: ZoomLevel

    @validator("end_date")
    def validate_dates(cls, end_date, values):
        if "start_date" in values and end_date < values["start_date"]:
            raise ValueError("End date must be after start date")
        return end_date

class EventCreate(EventBase):
    """Schema for creating new events"""
    pass

class EventUpdate(BaseModel):
    """Schema for updating events"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    location: Optional[Location] = None
    zoom_level: Optional[ZoomLevel] = None

class Event(EventBase):
    """Complete event model with ID"""
    id: str

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ZoomLevel: lambda v: v.value
        }
