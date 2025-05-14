from typing import List, Optional
from pymongo.database import Database
from core.repository import BaseRepository
from schemas.period_schemas import Period, PeriodCreate, PeriodUpdate
from pymongo.errors import PyMongoError
import logging
from fastapi.logger import logger
from bson import ObjectId

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
        try:
            result = self.collection.find_one({"name": name})
            return Period(**result) if result else None
        except PyMongoError as e:
            logger.error(f"Failed to get period by name {name}", exc_info=True)
            raise

    def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Period]:
        """Search periods by name or description with pagination"""
        try:
            # Validate pagination parameters
            skip = max(0, skip)
            limit = min(100, max(1, limit))
            
            results = self.collection.find(
                {"$text": {"$search": query}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})])
            
            return [Period(**doc) for doc in results.skip(skip).limit(limit)]
        except PyMongoError as e:
            logger.error(f"Failed to search periods with query {query}", exc_info=True)
            raise

    def get_by_year_range(self, year: int) -> List[Period]:
        """Get periods that include the specified year"""
        try:
            results = self.collection.find({
                "start_year": {"$lte": year},
                "end_year": {"$gte": year}
            })
            return [Period(**doc) for doc in results]
        except PyMongoError as e:
            logger.error(f"Failed to get periods for year {year}", exc_info=True)
            raise

    def create(self, period: PeriodCreate) -> Period:
        """Create new period with validation"""
        try:
            period_dict = period.dict()
            result = self.collection.insert_one(period_dict)
            created_period = self.get(str(result.inserted_id))
            
            # Clear relevant caches
            if hasattr(self, 'cache'):
                self.cache.delete("periods:*")
                
            return created_period
        except PyMongoError as e:
            logger.error("Failed to create period", exc_info=True)
            raise

    def query_periods(self,
                    field_queries: Optional[dict] = None,
                    skip: int = 0,
                    limit: int = 100) -> List[Period]:
        """
        Flexible query periods with:
        - Arbitrary field queries (exact or fuzzy matching)
        - Pagination
        
        Args:
            field_queries: Dict of {field: value} to query
                           String fields use fuzzy matching
                           Other fields use exact matching
            skip: Pagination offset
            limit: Maximum results per page
        """
        try:
            query = {}
            
            # Process field queries
            if field_queries:
                for field, value in field_queries.items():
                    if isinstance(value, str):
                        # Fuzzy match for string fields
                        query[field] = {"$regex": value, "$options": "i"}
                    else:
                        # Exact match for other types
                        query[field] = value
                
            # Validate pagination
            skip = max(0, skip)
            limit = min(100, max(1, limit))
            
            results = self.collection.find(query).skip(skip).limit(limit)
            return [period for doc in results if (period := self.safe_convert_to_period(doc))]
            
        except PyMongoError as e:
            logger.error("Failed to query periods", exc_info=True)
            raise
