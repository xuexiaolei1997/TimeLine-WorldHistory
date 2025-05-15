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
        """Advanced event search with multiple filters"""
        try:
            filter_query = {}
            
            # Text search
            if query:
                results = self.repository.search_text(query)
                return [Event(**doc) for doc in results[skip:skip+limit]]
            
            # Period filter
            if period:
                filter_query["period"] = period
                
            # Date range
            if start_date or end_date:
                date_query = {}
                if start_date:
                    date_query["$gte"] = start_date
                if end_date:
                    date_query["$lte"] = end_date
                filter_query["date.start"] = date_query
            
            # Tags filter
            if tags:
                filter_query["tags.keywords"] = {"$in": tags}
            
            # Importance filter
            if importance_min:
                filter_query["importance"] = {"$gte": importance_min}
            
            # Public filter
            if is_public is not None:
                filter_query["is_public"] = is_public
            
            # Region filter
            if region_name:
                filter_query["location.region_name"] = {"$regex": region_name, "$options": "i"}
            
            # Execute query
            results = self.repository.query_by_filters(filter_query)
            
            # Apply sorting
            if sort_by:
                results.sort(key=lambda x: x.get(sort_by, 0), reverse=sort_order < 0)
            else:
                # Default sorting by importance and date
                results.sort(key=lambda x: (
                    -x.get("importance", 0),
                    -datetime.strptime(x["date"]["start"], "%Y-%m-%d").timestamp()
                ))
            
            return [Event(**doc) for doc in results[skip:skip+limit]]
            
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
        """Create new event with timestamps"""
        try:
            event_dict = event.dict()
            event_dict["created_at"] = datetime.now()
            event_dict["last_updated"] = datetime.now()
            
            created = super().create(event)
            
            # Clear relevant caches
            if hasattr(self.repository, 'cache'):
                self.repository.cache.delete("events:*")
                
            return created
        except PyMongoError as e:
            logger.error("Failed to create event", exc_info=True)
            raise DatabaseError({
                "message": "Failed to create event",
                "details": {"error": str(e)}
            })

    def update(self, id: str, event: EventUpdate) -> Event:
        """Update event with timestamp"""
        try:
            event_dict = event.dict(exclude_unset=True)
            event_dict["last_updated"] = datetime.now()
            
            updated = super().update(id, event)
            
            # Clear relevant caches
            if hasattr(self.repository, 'cache'):
                self.repository.cache.delete(f"events:{id}")
                self.repository.cache.delete("events:*")
                
            return updated
        except PyMongoError as e:
            logger.error(f"Failed to update event {id}", exc_info=True)
            raise DatabaseError({
                "message": "Failed to update event",
                "details": {"error": str(e)}
            })
