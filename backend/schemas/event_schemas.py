from pydantic import BaseModel, Field, validator
from typing import Optional, List, Union
from datetime import datetime
from enum import Enum

class EventPeriod(str, Enum):
    ANCIENT = "ancient"
    MEDIEVAL = "medieval"
    MODERN = "modern"
    CONTEMPORARY = "contemporary"

class EventTitle(BaseModel):
    en: Optional[str] = Field(default="", max_length=200)
    zh: Optional[str] = Field(default="", max_length=200)
    
class EventDate(BaseModel):
    start: Optional[str] = Field(None, description="Format: YYYY-MM-DD")
    end: Optional[str] = Field(None, description="Format: YYYY-MM-DD")
    
    @validator('start', 'end')
    def validate_date_format(cls, v):
        if v is None:
            return v
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            return None  # 如果日期格式不正确，返回None而不是报错

class EventLocation(BaseModel):
    coordinates: List[float] = Field(default_factory=lambda: [0.0, 0.0])
    zoomLevel: int = Field(default=1)
    highlightColor: str = Field(default="#FF0000")
    region_name: Optional[str] = None

class EventMedia(BaseModel):
    images: List[str] = Field(default_factory=list)
    videos: List[str] = Field(default_factory=list)
    audios: List[str] = Field(default_factory=list)
    thumbnail: Optional[str] = None

class EventDescription(BaseModel):
    en: Optional[str] = Field(default="")
    zh: Optional[str] = Field(default="")

class ContentRef(BaseModel):
    type: str = Field(default="article")
    url: str = Field(default="")
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
    title: Union[EventTitle, dict] = Field(default_factory=EventTitle)
    period: Optional[EventPeriod] = Field(default=EventPeriod.MODERN)
    date: Union[EventDate, dict] = Field(default_factory=EventDate)
    location: Union[EventLocation, dict] = Field(default_factory=EventLocation)
    description: Union[EventDescription, dict] = Field(default_factory=EventDescription)
    media: Union[EventMedia, dict] = Field(default_factory=EventMedia)
    contentRefs: Union[ContentRefs, dict] = Field(default_factory=ContentRefs)
    tags: Union[EventTags, dict] = Field(default_factory=EventTags)
    importance: int = Field(default=1)
    is_public: bool = Field(default=True)
    last_updated: datetime = Field(default_factory=datetime.now)

    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True

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
        populate_by_name = True
