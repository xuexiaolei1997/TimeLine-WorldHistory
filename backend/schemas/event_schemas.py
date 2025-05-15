from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class EventPeriod(str, Enum):
    ANCIENT = "ancient"
    MEDIEVAL = "medieval"
    MODERN = "modern"
    CONTEMPORARY = "contemporary"

class EventTitle(BaseModel):
    en: str = Field(..., min_length=1, max_length=200)
    zh: str = Field(..., min_length=1, max_length=200)
    
class EventDate(BaseModel):
    start: str = Field(..., description="Format: YYYY-MM-DD")
    end: str = Field(..., description="Format: YYYY-MM-DD")
    
    @validator('start', 'end')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')

class EventLocation(BaseModel):
    coordinates: List[float] = Field(..., min_items=2, max_items=2)
    zoomLevel: int = Field(..., ge=1, le=20)
    highlightColor: str = Field(default="#FF0000", pattern="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")
    region_name: Optional[str] = None

class EventMedia(BaseModel):
    images: List[str] = Field(default_factory=list)
    videos: List[str] = Field(default_factory=list)
    audios: List[str] = Field(default_factory=list)
    thumbnail: Optional[str] = None

class EventDescription(BaseModel):
    en: str = Field(..., min_length=1)
    zh: str = Field(..., min_length=1)

class ContentRef(BaseModel):
    type: str = Field(..., pattern="^(article|image|video|document)$")
    url: str
    title: Optional[str] = None
    description: Optional[str] = None

class ContentRefs(BaseModel):
    articles: List[ContentRef] = Field(default_factory=list)
    images: List[ContentRef] = Field(default_factory=list)
    videos: List[ContentRef] = Field(default_factory=list)
    documents: List[ContentRef] = Field(default_factory=list)

class EventTags(BaseModel):
    category: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)

class EventBase(BaseModel):
    title: EventTitle
    period: EventPeriod
    date: EventDate
    location: EventLocation
    description: EventDescription
    media: EventMedia = Field(default_factory=EventMedia)
    contentRefs: ContentRefs = Field(default_factory=ContentRefs)
    tags: EventTags = Field(default_factory=EventTags)
    importance: int = Field(default=1, ge=1, le=5)
    is_public: bool = Field(default=True)
    last_updated: datetime = Field(default_factory=datetime.now)

class EventCreate(EventBase):
    pass

class EventUpdate(EventBase):
    pass

class Event(EventBase):
    id: str = Field(..., alias="_id")
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        allow_population_by_field_name = True
