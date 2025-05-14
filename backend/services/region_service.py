from typing import List, Optional
from pymongo.database import Database
from core.repository import BaseRepository
from schemas.region_schemas import Region, RegionCreate, RegionUpdate
from pymongo.errors import PyMongoError
import logging
from fastapi.logger import logger
from bson import ObjectId

class RegionRepository(BaseRepository[Region]):
    """Repository for region data operations"""
    
    def __init__(self, db: Database):
        super().__init__("regions", db)
        # Create 2dsphere index for geospatial queries
        self.collection.create_index([("boundary.coordinates", "2dsphere")])
        # Initialize cache reference
        self.cache = None

    def get_by_name(self, name: str) -> Optional[Region]:
        """Get region by exact name match"""
        try:
            result = self.collection.find_one({"name.en": name})
            return Region(**result) if result else None
        except PyMongoError as e:
            logger.error(f"Failed to get region by name {name}", exc_info=True)
            raise

    def get_by_period(self, period_id: str) -> List[Region]:
        """Get all regions associated with a period"""
        try:
            results = self.collection.find({"period_id": period_id})
            return [Region(**doc) for doc in results]
        except PyMongoError as e:
            logger.error(f"Failed to get regions for period {period_id}", exc_info=True)
            raise

    def find_within(self, coordinates: List[List[float]]) -> List[Region]:
        """Find regions that contain the given point"""
        try:
            results = self.collection.find({
                "boundary.coordinates": {
                    "$geoIntersects": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": coordinates
                        }
                    }
                }
            })
            return [Region(**doc) for doc in results]
        except PyMongoError as e:
            logger.error(f"Failed to find regions containing point {coordinates}", exc_info=True)
            raise

    def create(self, region: RegionCreate) -> Region:
        """Create new region with validation"""
        try:
            region_dict = region.dict()
            result = self.collection.insert_one(region_dict)
            created_region = self.get(str(result.inserted_id))
            
            # Clear relevant caches
            if hasattr(self, 'cache'):
                self.cache.delete("regions:*")
                
            return created_region
        except PyMongoError as e:
            logger.error("Failed to create region", exc_info=True)
            raise

    def query_regions(self,
                    field_queries: Optional[dict] = None,
                    skip: int = 0,
                    limit: int = 100) -> List[Region]:
        """
        Flexible query regions with:
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
            return [Region(**doc) for doc in results]
            
        except PyMongoError as e:
            logger.error("Failed to query regions", exc_info=True)
            raise
