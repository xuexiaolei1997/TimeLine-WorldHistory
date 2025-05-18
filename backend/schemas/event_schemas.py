from pydantic import BaseModel, Field, validator, HttpUrl
from typing import Optional, List, Union
from datetime import datetime
from enum import Enum

class EventPeriod(str, Enum):
    """历史时期枚举"""
    ANCIENT = "ancient"      # 古代
    MEDIEVAL = "medieval"    # 中世纪
    MODERN = "modern"        # 近代
    CONTEMPORARY = "contemporary"  # 现代
    PREHISTORIC = "prehistoric"    # 史前
    RENAISSANCE = "renaissance"    # 文艺复兴

class EventTitle(BaseModel):
    """事件标题(多语言)"""
    en: Optional[str] = Field(default="", max_length=200, description="英文标题")
    zh: Optional[str] = Field(default="", max_length=200, description="中文标题")
    
class EventDate(BaseModel):
    """事件日期范围"""
    start: Optional[str] = Field(
        None, 
        description="开始日期，格式: YYYY-MM-DD",
        pattern=r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"
    )
    end: Optional[str] = Field(
        None, 
        description="结束日期，格式: YYYY-MM-DD",
        pattern=r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"
    )
    
    @validator('end')
    def validate_end_date(cls, v, values):
        """验证结束日期不小于开始日期"""
        if 'start' in values and v and values['start']:
            if datetime.strptime(v, '%Y-%m-%d') < datetime.strptime(values['start'], '%Y-%m-%d'):
                raise ValueError("结束日期不能早于开始日期")
        return v

class EventLocation(BaseModel):
    """事件地理位置信息"""
    coordinates: List[float] = Field(
        default_factory=lambda: [0.0, 0.0],
        description="经纬度坐标 [经度, 纬度]",
        min_items=2,
        max_items=2
    )
    zoomLevel: int = Field(
        default=1,
        description="地图缩放级别",
        ge=1,
        le=20
    )
    highlightColor: str = Field(
        default="#FF0000",
        description="高亮颜色(十六进制)",
        pattern=r"^#[0-9a-fA-F]{6}$"
    )
    region_name: Optional[str] = Field(
        None,
        description="所属地区名称",
        max_length=100
    )

class EventMedia(BaseModel):
    """事件媒体资源"""
    images: List[HttpUrl] = Field(
        default_factory=list,
        description="图片URL列表"
    )
    videos: List[HttpUrl] = Field(
        default_factory=list,
        description="视频URL列表"
    )
    audios: List[HttpUrl] = Field(
        default_factory=list,
        description="音频URL列表"
    )
    thumbnail: Optional[HttpUrl] = Field(
        None,
        description="缩略图URL"
    )

class EventDescription(BaseModel):
    """事件描述(多语言)"""
    en: Optional[str] = Field(
        default="",
        description="英文描述",
        max_length=5000
    )
    zh: Optional[str] = Field(
        default="",
        description="中文描述",
        max_length=5000
    )

class ContentRef(BaseModel):
    """相关内容引用"""
    type: str = Field(
        default="article",
        description="内容类型: article|image|video|document",
        pattern=r"^(article|image|video|document)$"
    )
    url: HttpUrl = Field(
        ...,
        description="内容URL"
    )
    title: Optional[str] = Field(
        None,
        description="内容标题",
        max_length=200
    )
    description: Optional[str] = Field(
        None,
        description="内容描述",
        max_length=1000
    )

class ContentRefs(BaseModel):
    """事件相关内容引用集合"""
    articles: List[ContentRef] = Field(
        default_factory=list,
        description="相关文章"
    )
    images: List[ContentRef] = Field(
        default_factory=list,
        description="相关图片"
    )
    videos: List[ContentRef] = Field(
        default_factory=list,
        description="相关视频"
    )
    documents: List[ContentRef] = Field(
        default_factory=list,
        description="相关文档"
    )

class EventTags(BaseModel):
    """事件标签分类"""
    category: List[str] = Field(
        default_factory=list,
        description="分类标签",
        max_items=5
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="关键词标签",
        max_items=20
    )

class EventBase(BaseModel):
    """事件基础模型"""
    title: Union[EventTitle, dict] = Field(
        default_factory=EventTitle,
        description="事件标题"
    )
    period: Optional[EventPeriod] = Field(
        default=EventPeriod.MODERN,
        description="所属历史时期"
    )
    date: Union[EventDate, dict] = Field(
        default_factory=EventDate,
        description="事件日期范围"
    )
    location: Union[EventLocation, dict] = Field(
        default_factory=EventLocation,
        description="地理位置信息"
    )
    description: Union[EventDescription, dict] = Field(
        default_factory=EventDescription,
        description="事件描述"
    )
    media: Union[EventMedia, dict] = Field(
        default_factory=EventMedia,
        description="媒体资源"
    )
    contentRefs: Union[ContentRefs, dict] = Field(
        default_factory=ContentRefs,
        description="相关内容引用"
    )
    tags: Union[EventTags, dict] = Field(
        default_factory=EventTags,
        description="标签分类"
    )
    importance: int = Field(
        default=1,
        description="重要性(1-5)",
        ge=1,
        le=5
    )
    is_public: bool = Field(
        default=True,
        description="是否公开"
    )
    last_updated: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="最后更新时间"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
        description="创建时间"
    )

    class Config:
        """Pydantic配置"""
        validate_assignment = True  # 赋值时验证
        arbitrary_types_allowed = True  # 允许任意类型
        json_schema_extra = {
            "example": {
                "title": {"en": "Sample Event", "zh": "示例事件"},
                "period": "modern",
                "date": {"start": "2023-01-01", "end": "2023-12-31"},
                "location": {
                    "coordinates": [116.404, 39.915],
                    "zoomLevel": 5,
                    "highlightColor": "#FF0000",
                    "region_name": "Beijing"
                },
                "description": {
                    "en": "Sample event description",
                    "zh": "示例事件描述"
                },
                "media": {
                    "images": ["https://example.com/image.jpg"],
                    "thumbnail": "https://example.com/thumb.jpg"
                },
                "tags": {
                    "category": ["sample"],
                    "keywords": ["demo"]
                },
                "importance": 3,
                "is_public": True
            }
        }

class EventCreate(EventBase):
    """创建事件模型"""
    pass

class EventUpdate(EventBase):
    """更新事件模型"""
    pass

class Event(EventBase):
    """事件完整模型(包含ID)"""
    id: str = Field(..., alias="_id", description="事件ID")

    class Config:
        """Pydantic配置"""
        from_attributes = True  # 支持ORM模式
        populate_by_name = True  # 允许通过字段名或别名填充
        json_encoders = {
            datetime: lambda v: v.isoformat()  # 日期时间序列化为ISO格式
        }
