from typing import List, Optional, Dict, Any
from pymongo.database import Database
from pymongo.errors import PyMongoError
from datetime import datetime
import logging
from fastapi.logger import logger
from bson import ObjectId

from core.repository import BaseRepository
from core.service import BaseService
from schemas.event_schemas import Event, EventCreate, EventUpdate
from core.exceptions import DatabaseError, NotFoundError

class EventRepository(BaseRepository[Event]):
    """Repository for event data operations"""
    
    def __init__(self, db: Database):
        super().__init__("events", db)
        # Create indexes for better performance
        self.collection.create_index([
            ("title.en", "text"), 
            ("title.zh", "text"),
            ("description.en", "text"),
            ("description.zh", "text"),
            ("tags.keywords", "text")
        ])
        self.collection.create_index([("date.start", 1)])
        self.collection.create_index([("date.end", 1)])
        self.collection.create_index([("period", 1)])
        self.collection.create_index([("importance", -1)])
        self.collection.create_index([("is_public", 1)])
        # Initialize cache reference
        self.cache = None

    def search_text(self, query: str) -> List[Dict[str, Any]]:
        """Basic text search"""
        return list(self.collection.find(
            {"$text": {"$search": query}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]))

    def query_by_filters(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query with arbitrary filters"""
        return list(self.collection.find(filters))

    def get_by_period(self, period: str) -> List[Dict[str, Any]]:
        """Get events by period"""
        return list(self.collection.find({"period": period}))

    def get_by_date_range(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get events by date range"""
        return list(self.collection.find({
            "date.start": {"$gte": start_date},
            "date.end": {"$lte": end_date}
        }))

    def get_by_region(self, region_name: str) -> List[Dict[str, Any]]:
        """Get events by region"""
        return list(self.collection.find({
            "location.region_name": {"$regex": region_name, "$options": "i"}
        }))

class EventService(BaseService[Event, EventCreate, EventUpdate]):
    """Service layer for event operations"""
    
    def __init__(self, repository: EventRepository):
        super().__init__(repository)
        self.repository = repository

    def search_events(self, 
                    query: str = None,
                    period: str = None,
                    start_date: str = None,
                    end_date: str = None,
                    tags: List[str] = None,
                    importance_min: int = None,
                    is_public: bool = None,
                    region_name: str = None,
                    skip: int = 0,
                    limit: int = 50,
                    sort_by: str = None,
                    sort_order: int = 1) -> List[Event]:
        """高级事件搜索(带缓存)
        Args:
            query: 文本搜索关键字
            period: 时期过滤(对应EventPeriod枚举值)
            start_date: 开始日期(YYYY-MM-DD格式)
            end_date: 结束日期(YYYY-MM-DD格式)
            tags: 标签过滤列表
            importance_min: 最小重要性(1-5)
            is_public: 是否只获取公开事件
            region_name: 地区名称(不区分大小写)
            skip: 跳过记录数(分页用)
            limit: 返回记录数(最大100)
            sort_by: 排序字段(如"date.start")
            sort_order: 排序顺序(1升序,-1降序)
        Returns:
            List[Event]: 匹配的事件列表(已转换的Event模型)
        Notes:
            1. 使用Redis缓存查询结果(5分钟TTL)
            2. 缓存键包含所有查询参数
            3. 文本搜索优先于其他过滤条件
        """
        try:
            # 生成缓存键
            cache_key = f"events:search:{query}:{period}:{start_date}:{end_date}:" \
                       f"{':'.join(tags) if tags else ''}:{importance_min}:" \
                       f"{is_public}:{region_name}:{skip}:{limit}:{sort_by}:{sort_order}"
            
            # 尝试从缓存获取
            if hasattr(self.repository, 'cache'):
                cached = self.repository.cache.get(cache_key)
                if cached is not None:
                    return cached
            
            filter_query = {}
            
            # 文本搜索
            if query:
                results = self.repository.search_text(query)
                events = [Event(**doc) for doc in results[skip:skip+limit]]
            else:
                # 时期过滤
                if period:
                    filter_query["period"] = period
                    
                # 日期范围
                if start_date or end_date:
                    date_query = {}
                    if start_date:
                        date_query["$gte"] = start_date
                    if end_date:
                        date_query["$lte"] = end_date
                    filter_query["date.start"] = date_query
                
                # 标签过滤
                if tags:
                    filter_query["tags.keywords"] = {"$in": tags}
                
                # 重要性过滤
                if importance_min:
                    filter_query["importance"] = {"$gte": importance_min}
                
                # 公开状态过滤
                if is_public is not None:
                    filter_query["is_public"] = is_public
                
                # 地区过滤
                if region_name:
                    filter_query["location.region_name"] = {"$regex": region_name, "$options": "i"}
                
                # 执行查询
                results = self.repository.query_by_filters(filter_query)
                
                # 应用排序
                if sort_by:
                    results.sort(key=lambda x: x.get(sort_by, 0), reverse=sort_order < 0)
                else:
                    # 默认按重要性和日期排序
                    results.sort(key=lambda x: (
                        -x.get("importance", 0),
                        -datetime.strptime(x["date"]["start"], "%Y-%m-%d").timestamp()
                    ))
                
                events = [Event(**doc) for doc in results[skip:skip+limit]]
            
            # 缓存结果(5分钟)
            if hasattr(self.repository, 'cache'):
                self.repository.cache.set(cache_key, events, ttl=300)
            
            return events
            
        except PyMongoError as e:
            logger.error(f"Failed to search events: {str(e)}", exc_info=True)
            raise DatabaseError({
                "message": "Failed to search events",
                "details": {"error": str(e)}
            })

    def get_by_period(self, period: str) -> List[Event]:
        """Get events by period"""
        try:
            results = self.repository.get_by_period(period)
            return [Event(**doc) for doc in results]
        except PyMongoError as e:
            logger.error(f"Failed to get events by period {period}", exc_info=True)
            raise DatabaseError({
                "message": "Failed to get events by period",
                "details": {"error": str(e)}
            })

    def get_by_date_range(self, start_date: str, end_date: str) -> List[Event]:
        """Get events by date range"""
        try:
            results = self.repository.get_by_date_range(start_date, end_date)
            return [Event(**doc) for doc in results]
        except PyMongoError as e:
            logger.error("Failed to get events by date range", exc_info=True)
            raise DatabaseError({
                "message": "Failed to get events by date range",
                "details": {"error": str(e)}
            })

    def get_by_region(self, region_name: str) -> List[Event]:
        """Get events by region"""
        try:
            results = self.repository.get_by_region(region_name)
            return [Event(**doc) for doc in results]
        except PyMongoError as e:
            logger.error(f"Failed to get events by region {region_name}", exc_info=True)
            raise DatabaseError({
                "message": "Failed to get events by region",
                "details": {"error": str(e)}
            })

    def create(self, event: EventCreate) -> Event:
        """创建新事件
        Args:
            event: 事件创建模型
        Returns:
            Event: 创建的事件对象
        Notes:
            1. 自动设置创建时间和最后更新时间
            2. 创建成功后清除相关缓存:
               - 所有事件列表缓存
               - 对应时期的缓存
               - 对应地区的缓存(如果设置了region_name)
        """
        try:
            event_dict = event.dict()
            event_dict["created_at"] = datetime.now()
            event_dict["last_updated"] = datetime.now()
            
            created = super().create(event)
            
            # 清除相关缓存
            if hasattr(self.repository, 'cache'):
                # 清除所有事件列表缓存
                self.repository.cache.delete("events:list:*")
                # 清除按时期分类的缓存
                self.repository.cache.delete(f"events:period:{event.period}")
                # 清除按地区分类的缓存
                if event.location and event.location.get('region_name'):
                    self.repository.cache.delete(f"events:region:{event.location['region_name']}")
                
            return created
        except PyMongoError as e:
            logger.error("Failed to create event", exc_info=True)
            raise DatabaseError({
                "message": "Failed to create event",
                "details": {"error": str(e)}
            })

    def update(self, id: str, event: EventUpdate) -> Event:
        """更新事件
        Args:
            id: 事件ID
            event: 事件更新模型
        Returns:
            Event: 更新后的事件对象
        Notes:
            1. 自动更新最后修改时间
            2. 更新成功后清除相关缓存:
               - 该事件的单独缓存
               - 所有事件列表缓存
               - 如果时期变更: 清除新旧时期的缓存
               - 如果地区变更: 清除新旧地区的缓存
            3. 只更新提供的字段(部分更新)
        """
        try:
            # 先获取旧数据用于缓存清理
            old_event = self.get(id)
            
            event_dict = event.dict(exclude_unset=True)
            event_dict["last_updated"] = datetime.now()
            
            updated = super().update(id, event)
            
            # 清除相关缓存
            if hasattr(self.repository, 'cache'):
                # 清除单个事件缓存
                self.repository.cache.delete(f"events:{id}")
                # 清除所有事件列表缓存
                self.repository.cache.delete("events:list:*")
                # 如果时期发生变化，清除旧时期缓存
                if 'period' in event_dict and event_dict['period'] != old_event.period:
                    self.repository.cache.delete(f"events:period:{old_event.period}")
                # 清除新时期的缓存
                self.repository.cache.delete(f"events:period:{updated.period}")
                # 如果地区发生变化，清除旧地区缓存
                if 'location' in event_dict and event_dict['location'].get('region_name') != old_event.location.region_name:
                    if old_event.location.region_name:
                        self.repository.cache.delete(f"events:region:{old_event.location.region_name}")
                # 清除新地区的缓存
                if updated.location.region_name:
                    self.repository.cache.delete(f"events:region:{updated.location.region_name}")
                
            return updated
        except PyMongoError as e:
            logger.error(f"Failed to update event {id}", exc_info=True)
            raise DatabaseError({
                "message": "Failed to update event",
                "details": {"error": str(e)}
            })
