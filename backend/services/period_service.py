from typing import List, Optional, Dict
from pymongo.database import Database
from core.repository import BaseRepository
from core.service import BaseService
from schemas.period_schemas import Period, PeriodCreate, PeriodUpdate
from pymongo.errors import PyMongoError
import logging
from fastapi.logger import logger

class PeriodRepository(BaseRepository[Period]):
    """Repository for period data operations"""
    
    def __init__(self, db: Database):
        super().__init__("periods", db)
        # Ensure indexes for better query performance
        self.collection.create_index([("name", "text"), ("description", "text")])
        # Initialize cache reference
        self.cache = None

    def get_by_name(self, name: str) -> Optional[Period]:
        """Get period by exact name match"""
        return self.collection.find_one({"name": name})

    def search(self, query: str) -> List[Period]:
        """Search periods by name or description"""
        return list(self.collection.find(
            {"$text": {"$search": query}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]))

    def get_by_year_range(self, year: int) -> List[Period]:
        """Get periods that include the specified year"""
        return list(self.collection.find({
            "start_year": {"$lte": year},
            "end_year": {"$gte": year}
        }))

    def query_by_fields(self, field_queries: Dict[str, str]) -> List[Period]:
        """Query periods by arbitrary field filters"""
        query = {}
        for field, value in field_queries.items():
            if isinstance(value, str):
                query[field] = {"$regex": value, "$options": "i"}
            else:
                query[field] = value
        return list(self.collection.find(query))

class PeriodService(BaseService[Period, PeriodCreate, PeriodUpdate]):
    """Service layer for period operations"""
    
    def __init__(self, repository: PeriodRepository):
        super().__init__(repository)
        self.repository = repository

    def get_by_name(self, name: str) -> Optional[Period]:
        """Get period by exact name match"""
        try:
            result = self.repository.get_by_name(name)
            if not result:
                return None
            return Period(**result)
        except PyMongoError as e:
            logger.error(f"Failed to get period by name {name}", exc_info=True)
            raise

    def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Period]:
        """Search periods with pagination"""
        try:
            skip = max(0, skip)
            limit = min(100, max(1, limit))
            results = self.repository.search(query)
            return [Period(**doc) for doc in results[skip:skip+limit]]
        except PyMongoError as e:
            logger.error(f"Failed to search periods with query {query}", exc_info=True)
            raise

    def get_by_year_range(self, year: int) -> List[Period]:
        """Get periods that include the specified year"""
        try:
            results = self.repository.get_by_year_range(year)
            return [Period(**doc) for doc in results]
        except PyMongoError as e:
            logger.error(f"Failed to get periods for year {year}", exc_info=True)
            raise

    def query_periods(self,
                    field_queries: Optional[Dict[str, str]] = None,
                    skip: int = 0,
                    limit: int = 100) -> List[Period]:
        """Flexible query with field filters and pagination"""
        try:
            skip = max(0, skip)
            limit = min(100, max(1, limit))
            
            if not field_queries:
                field_queries = {}
                
            results = self.repository.query_by_fields(field_queries)
            return [Period(**doc) for doc in results[skip:skip+limit]]
        except PyMongoError as e:
            logger.error("Failed to query periods", exc_info=True)
            raise
