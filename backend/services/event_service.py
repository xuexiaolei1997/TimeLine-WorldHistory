from typing import List, Optional, Dict, Any
from pymongo.database import Database
from pymongo.errors import PyMongoError
from datetime import datetime
from fastapi.logger import logger
from bson import ObjectId

from core.repository import BaseRepository
from schemas.event_schemas import Event, EventCreate, EventUpdate

class EventRepository(BaseRepository[Event]):
    """Repository for event data operations"""
    
    def __init__(self, db: Database):
        super().__init__("events", db)
        # 创建索引以提升查询性能
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
        """
        高级搜索功能
        """
        try:
            filter_query = {}
            
            # 文本搜索
            if query:
                filter_query["$text"] = {"$search": query}
            
            # 时期筛选
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
            
            # 标签筛选
            if tags:
                filter_query["tags.keywords"] = {"$in": tags}
            
            # 重要性筛选
            if importance_min:
                filter_query["importance"] = {"$gte": importance_min}
            
            # 公开性筛选
            if is_public is not None:
                filter_query["is_public"] = is_public
            
            # 区域筛选
            if region_name:
                filter_query["location.region_name"] = {"$regex": region_name, "$options": "i"}
            
            # 排序
            sort_options = {}
            if sort_by:
                sort_options[sort_by] = sort_order
            else:
                # 默认按重要性和日期排序
                sort_options = {
                    "importance": -1,
                    "date.start": -1
                }
            
            # 执行查询
            cursor = self.collection.find(
                filter_query,
                skip=skip,
                limit=limit
            ).sort(list(sort_options.items()))
            
            return [self._convert_id(doc) for doc in cursor]
            
        except PyMongoError as e:
            logger.error(f"Failed to search events: {str(e)}", exc_info=True)
            raise

    def get_by_period(self, period: str) -> List[Event]:
        """按时期获取事件"""
        try:
            cursor = self.collection.find({"period": period})
            return [self._convert_id(doc) for doc in cursor]
        except PyMongoError as e:
            logger.error(f"Failed to get events by period {period}", exc_info=True)
            raise

    def get_by_date_range(self, start_date: str, end_date: str) -> List[Event]:
        """按日期范围获取事件"""
        try:
            cursor = self.collection.find({
                "date.start": {"$gte": start_date},
                "date.end": {"$lte": end_date}
            })
            return [self._convert_id(doc) for doc in cursor]
        except PyMongoError as e:
            logger.error(f"Failed to get events by date range", exc_info=True)
            raise

    def get_by_region(self, region_name: str) -> List[Event]:
        """按区域获取事件"""
        try:
            cursor = self.collection.find({
                "location.region_name": {"$regex": region_name, "$options": "i"}
            })
            return [self._convert_id(doc) for doc in cursor]
        except PyMongoError as e:
            logger.error(f"Failed to get events by region {region_name}", exc_info=True)
            raise

    def create(self, event: EventCreate) -> Event:
        """创建新事件"""
        try:
            event_dict = event.dict()
            event_dict["created_at"] = datetime.now()
            event_dict["last_updated"] = datetime.now()
            
            result = self.collection.insert_one(event_dict)
            return self.get(str(result.inserted_id))
        except PyMongoError as e:
            logger.error("Failed to create event", exc_info=True)
            raise

    def update(self, id: str, event: EventUpdate) -> Optional[Event]:
        """更新事件"""
        try:
            event_dict = event.dict(exclude_unset=True)
            event_dict["last_updated"] = datetime.now()
            
            result = self.collection.update_one(
                {"_id": ObjectId(id)},
                {"$set": event_dict}
            )
            
            if result.modified_count == 0:
                return None
                
            return self.get(id)
        except PyMongoError as e:
            logger.error(f"Failed to update event {id}", exc_info=True)
            raise

    def _convert_id(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """转换 MongoDB _id 为字符串"""
        if doc and "_id" in doc:
            doc["id"] = str(doc.pop("_id"))
        return doc
