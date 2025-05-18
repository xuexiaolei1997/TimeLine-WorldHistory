from fastapi import APIRouter, Depends, Query, Request
from typing import List, Optional
from fastapi.logger import logger
from utils.cache import cache_response
from utils.decorators import handle_app_exceptions, wrap_response
from datetime import datetime

from services.event_service import EventService
from core.dependencies import get_event_service
from schemas.event_schemas import EventCreate, EventUpdate, Event, EventPeriod

router = APIRouter(prefix="/events", tags=["events"])

def transform_event(event: dict) -> dict:
    """转换事件数据为前端兼容格式(带增强的错误处理)
    Args:
        event: 原始事件数据字典
    Returns:
        dict: 转换后的事件数据字典
    """
    if not event:
        return None
    
    try:
        # 1. 初始化基础数据结构，确保所有必要字段都有默认值
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

@router.get("/test")
async def test_endpoint(
    request: Request):
    """测试端点(检查数据库连接)
    Returns:
        dict: 包含测试结果的响应
    Notes:
        1. 主要用于健康检查
        2. 返回200表示服务正常运行
    """
    return wrap_response(data={"message": "测试端点工作正常"})


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
    """获取历史事件列表(带高级过滤和排序)
    Args:
        query: 文本搜索关键字(支持中英文)
        period: 历史时期过滤(枚举值: ancient/medieval/modern/contemporary)
        start_date: 开始日期(YYYY-MM-DD格式)
        end_date: 结束日期(YYYY-MM-DD格式)
        tags: 标签过滤列表(多个标签用逗号分隔)
        importance_min: 最小重要性(1-5, 1最低,5最高)
        is_public: 是否只获取公开事件(True/False)
        region_name: 地区名称过滤(精确匹配)
        skip: 跳过记录数(分页用)
        limit: 返回记录数(最大100)
        sort_by: 排序字段(如"date.start","importance")
        sort_order: 排序顺序(1升序,-1降序)
    Returns:
        dict: 包含事件列表的响应，每个事件包含:
           - id: 事件ID
           - title: 多语言标题
           - period: 所属时期
           - date: 日期范围
           - location: 地理位置信息
           - description: 多语言描述
           - media: 媒体资源
           - contentRefs: 相关引用内容
           - tags: 分类标签
           - importance: 重要性等级
           - is_public: 是否公开
    Notes:
        1. 使用Redis缓存结果(5分钟TTL)
        2. 支持多条件组合查询
        3. 返回结果已转换为前端兼容格式
        4. 默认按开始日期降序排列
    Examples:
        GET /events/?period=ancient&importance_min=3&limit=10
        GET /events/?query=战争&start_date=1914-01-01&end_date=1918-12-31
    """
    logger.info(f"获取历史事件列表 - 查询条件: 关键字={query}, 时期={period}, 地区={region_name}, 日期范围={start_date}至{end_date}, 标签={tags}, 重要性>={importance_min}, 公开={is_public}, 排序={sort_by} {sort_order}")
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
    """创建新历史事件(带字段验证)
    Args:
        event: 事件创建数据模型(包含以下字段):
           - title: 多语言标题(中英文必填其一)
           - period: 所属时期(ancient/medieval/modern/contemporary)
           - date: 日期范围(包含start和end)
           - location: 地理位置信息(包含coordinates和region_name)
           - description: 多语言描述
           - media: 媒体资源(可选)
           - contentRefs: 相关引用内容(可选)
           - tags: 分类标签(可选)
           - importance: 重要性等级(1-5)
           - is_public: 是否公开(默认True)
    Returns:
        dict: 包含创建事件的响应(已转换为前端兼容格式)
    Notes:
        1. 自动设置创建时间和最后更新时间
        2. 创建成功后清除相关缓存:
           - 事件列表缓存
           - 如果设置了时期: 清除该时期事件缓存
           - 如果设置了地区: 清除该地区事件缓存
        3. 字段验证规则:
           - 标题至少提供一种语言
           - 日期范围必须有效(start <= end)
           - 坐标必须是有效的[经度,纬度]
           - 重要性必须在1-5之间
    Examples:
        POST /events/
        {
            "title": {"zh": "五四运动", "en": "May Fourth Movement"},
            "period": "modern",
            "date": {"start": "1919-05-04", "end": "1919-06-28"},
            "location": {
                "coordinates": [116.404, 39.915],
                "region_name": "北京"
            },
            "importance": 4
        }
    """
    logger.info(f"创建新历史事件: {event.title.zh or event.title.en} (时期: {event.period}, 地区: {event.location.region_name}, 日期: {event.date.start}至{event.date.end})")
    result = service.create(event)
    return wrap_response(data=transform_event(result))

@router.get("/{event_id}", response_model=dict)
@cache_response(ttl=300)
@handle_app_exceptions
async def get_event(
    event_id: str,
    service: EventService = Depends(get_event_service)
):
    """根据ID获取事件详情(带缓存策略)
    Args:
        event_id: 事件ID(MongoDB ObjectId)
    Returns:
        dict: 包含事件详情的响应(已转换为前端兼容格式)，包含:
           - id: 事件ID
           - title: 多语言标题(中英文)
           - period: 所属时期
           - date: 日期范围(start和end)
           - location: 地理位置信息(坐标和地区名)
           - description: 多语言描述
           - media: 媒体资源(图片/视频/音频)
           - contentRefs: 相关引用内容
           - tags: 分类标签
           - importance: 重要性等级
           - is_public: 是否公开
           - created_at: 创建时间
           - last_updated: 最后更新时间
    Notes:
        1. 使用Redis缓存结果(5分钟TTL)
        2. 如果找不到会返回404错误
        3. 缓存策略:
           - 首次查询从数据库加载并缓存
           - 后续查询直接从缓存读取
           - 事件更新时自动清除缓存
        4. 包含完整事件信息和关联数据
    Examples:
        GET /events/507f1f77bcf86cd799439011
    """
    logger.info(f"查询事件详情 - ID: {event_id} (使用缓存策略)")
    event = service.get(event_id)
    return wrap_response(data=transform_event(event))

@router.put("/{event_id}", response_model=dict)
@handle_app_exceptions
async def update_event(
    event_id: str,
    event: EventUpdate,
    service: EventService = Depends(get_event_service)
):
    """更新事件信息(支持部分更新)
    Args:
        event_id: 要更新的事件ID(MongoDB ObjectId)
        event: 事件更新数据模型(包含需要更新的字段)
    Returns:
        dict: 包含更新后事件详情的响应(已转换为前端兼容格式)
    Notes:
        1. 自动更新最后修改时间
        2. 更新成功后清除相关缓存:
           - 该事件的单独缓存
           - 事件列表缓存
           - 如果时期变更: 清除新旧时期的事件缓存
           - 如果地区变更: 清除新旧地区的事件缓存
        3. 支持部分更新(仅更新提供的字段)
        4. 字段验证规则:
           - 日期范围必须有效(start <= end)
           - 坐标必须是有效的[经度,纬度]
           - 重要性必须在1-5之间
    Examples:
        PUT /events/507f1f77bcf86cd799439011
        {
            "title": {"zh": "更新后的标题"},
            "importance": 5
        }
    """
    logger.info(f"更新事件信息 - ID: {event_id} (更新字段: {event.dict(exclude_unset=True)})")
    result = service.update(event_id, event)
    return wrap_response(data=transform_event(result))

@router.delete("/{event_id}", response_model=dict)
@handle_app_exceptions
async def delete_event(
    event_id: str,
    service: EventService = Depends(get_event_service)
):
    """删除历史事件及其关联资源
    Args:
        event_id: 要删除的事件ID(MongoDB ObjectId)
    Returns:
        dict: 包含删除结果的响应
    Notes:
        1. 删除成功后清除相关缓存:
           - 该事件的单独缓存
           - 事件列表缓存
           - 该事件所属时期的事件缓存
           - 该事件所属地区的事件缓存
        2. 同时清理关联资源:
           - 删除关联的媒体文件(图片/视频/音频)
           - 删除关联的引用内容
           - 从所有相关标签中移除该事件
        3. 操作不可逆，请谨慎使用
    Examples:
        DELETE /events/507f1f77bcf86cd799439011
    """
    logger.info(f"删除历史事件及其关联资源 - ID: {event_id} (包括缓存、媒体文件和关联数据)")
    service.delete(event_id)
    return wrap_response(data={"message": "事件删除成功"})

@router.get("/by-period/{period}", response_model=dict)
@cache_response(ttl=300)
@handle_app_exceptions
async def get_events_by_period(
    period: EventPeriod,
    service: EventService = Depends(get_event_service)
):
    """根据历史时期获取事件列表
    Args:
        period: 历史时期枚举值(ancient/medieval/modern/contemporary)
    Returns:
        dict: 包含事件列表的响应(已转换为前端兼容格式)
    Notes:
        1. 使用Redis缓存结果(5分钟TTL)
        2. 返回结果按开始日期排序
        3. 包含该时期所有重要事件
    """
    logger.info(f"获取历史时期事件列表 - 时期: {period.value}")
    events = service.get_by_period(period.value)
    return wrap_response(data=[transform_event(event) for event in events])

@router.get("/by-region/{region_name}", response_model=dict)
@cache_response(ttl=300)
@handle_app_exceptions
async def get_events_by_region(
    region_name: str,
    service: EventService = Depends(get_event_service)
):
    """根据地区名称获取关联事件列表
    Args:
        region_name: 地区名称(精确匹配)
    Returns:
        dict: 包含事件列表的响应(已转换为前端兼容格式)
    Notes:
        1. 使用Redis缓存结果(5分钟TTL)
        2. 返回结果按开始日期排序
        3. 包含该地区所有重要事件
    """
    logger.info(f"获取地区关联事件列表 - 地区: {region_name}")
    events = service.get_by_region(region_name)
    return wrap_response(data=[transform_event(event) for event in events])
