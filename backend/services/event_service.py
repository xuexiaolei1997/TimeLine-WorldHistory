from typing import List, Optional
from pymongo.database import Database
from core.repository import BaseRepository
from schemas.event_schemas import Event, EventCreate, EventUpdate
from pymongo.errors import PyMongoError
import logging
from fastapi.logger import logger
from bson import ObjectId

class EventRepository(BaseRepository[Event]):
    """Repository for event data operations"""
    
    def __init__(self, db: Database):
        super().__init__("events", db)
        # Ensure indexes for better query performance
        self.collection.create_index([("title", "text"), ("description", "text")])
        # Initialize cache reference
        self.cache = None

    def get_by_title(self, title: str) -> Optional[Event]:
        """Get event by exact title match"""
        try:
            result = self.collection.find_one({"title": title})
            return Event(**result) if result else None
        except PyMongoError as e:
            logger.error(f"Failed to get event by title {title}", exc_info=True)
            raise

    def get_by_region(self, region_id: str) -> List[Event]:
        """Get events by region ID"""
        try:
            results = self.collection.find({"region_id": region_id})
            return [Event(**doc) for doc in results]
        except PyMongoError as e:
            logger.error(f"Failed to get events for region {region_id}", exc_info=True)
            raise

    def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Event]:
        """Search events by title or description with pagination"""
        try:
            # Validate pagination parameters
            skip = max(0, skip)
            limit = min(100, max(1, limit))
            
            results = self.collection.find(
                {"$text": {"$search": query}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})])
            
            return [Event(**doc) for doc in results.skip(skip).limit(limit)]
        except PyMongoError as e:
            logger.error(f"Failed to search events with query {query}", exc_info=True)
            raise

    def create(self, event: EventCreate) -> Event:
        """Create new event with validation"""
        try:
            event_dict = event.dict()
            result = self.collection.insert_one(event_dict)
            created_event = self.get(str(result.inserted_id))
            
            # Clear relevant caches
            if hasattr(self, 'cache'):
                self.cache.delete("events:*")
                
            return created_event
        except PyMongoError as e:
            logger.error("Failed to create event", exc_info=True)
            raise

    def query_events(self,
                   field_queries: Optional[dict] = None,
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None,
                   region_id: Optional[str] = None,
                   skip: int = 0,
                   limit: int = 100) -> List[Event]:
        """
        Flexible query events with:
        - All field queries use fuzzy matching
        - Optional time range filtering
        - Pagination
        
        Args:
            field_queries: Dict of {field: value} to query (all fields use fuzzy matching)
            start_date: Optional minimum date (yyyy-mm-dd)
            end_date: Optional maximum date (yyyy-mm-dd)
            skip: Pagination offset
            limit: Maximum results per page
        """
        try:
            query = {}
            
            # Process field queries
            if field_queries:
                for field, value in field_queries.items():
                    if value is not None:
                        # Special handling for zoom level (numeric comparison)
                        if field == 'location.zoomLevel' and isinstance(value, dict):
                            query[field] = value
                        else:
                            # Default to fuzzy matching for strings
                            query[field] = {"$regex": str(value), "$options": "i"}
                
            # Handle optional date range
            if start_date or end_date:
                date_query = {}
                if start_date:
                    date_query["$gte"] = start_date
                if end_date:
                    date_query["$lte"] = end_date
                query["date.start"] = date_query
                
            # Handle region filter
            if region_id:
                query["region_id"] = region_id
                
            # Validate pagination
            skip = max(0, skip)
            limit = min(100, max(1, limit))
            
            results = self.collection.find(query).skip(skip).limit(limit)
            return [Event(**doc) for doc in results]
            
        except PyMongoError as e:
            logger.error("Failed to query events", exc_info=True)
            raise
