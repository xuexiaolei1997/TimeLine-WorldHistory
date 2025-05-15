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


from core.service import BaseService
from core.exceptions import DatabaseError

class RegionService(BaseService[Region, RegionCreate, RegionUpdate]):
    """Service layer for region business logic"""
    
    def __init__(self, repository: RegionRepository):
        super().__init__(repository)
        self.repository = repository

    def get_region(self, region_id: str) -> Optional[Region]:
        """Get a single region by ID"""
        try:
            return self.repository.get(region_id)
        except PyMongoError as e:
            logger.error(f"Failed to get region {region_id}", exc_info=True)
            raise DatabaseError({
                "message": "Failed to get region",
                "details": {"error": str(e)}
            })

    def get_regions_by_period(self, period_id: str) -> List[Region]:
        """Get all regions associated with a period"""
        try:
            return self.repository.get_by_period(period_id)
        except PyMongoError as e:
            logger.error(f"Failed to get regions for period {period_id}", exc_info=True)
            raise DatabaseError({
                "message": "Failed to get regions by period",
                "details": {"error": str(e)}
            })

    def find_regions_within(self, coordinates: List[List[float]]) -> List[Region]:
        """Find regions that contain the given coordinates"""
        try:
            return self.repository.find_within(coordinates)
        except PyMongoError as e:
            logger.error(f"Failed to find regions within {coordinates}", exc_info=True)
            raise DatabaseError({
                "message": "Failed to find regions within coordinates",
                "details": {"error": str(e)}
            })

    def create_region(self, region_data: RegionCreate) -> Region:
        """Create a new region"""
        try:
            created = super().create(region_data)
            if hasattr(self.repository, 'cache'):
                self.repository.cache.delete("regions:*")
            return created
        except PyMongoError as e:
            logger.error("Failed to create region", exc_info=True)
            raise DatabaseError({
                "message": "Failed to create region",
                "details": {"error": str(e)}
            })

    def update_region(self, region_id: str, region_data: RegionUpdate) -> Region:
        """Update an existing region"""
        try:
            updated = super().update(region_id, region_data)
            if hasattr(self.repository, 'cache'):
                self.repository.cache.delete(f"regions:{region_id}")
                self.repository.cache.delete("regions:*")
            return updated
        except PyMongoError as e:
            logger.error(f"Failed to update region {region_id}", exc_info=True)
            raise DatabaseError({
                "message": "Failed to update region",
                "details": {"error": str(e)}
            })

    def delete_region(self, region_id: str) -> bool:
        """Delete a region"""
        try:
            deleted = super().delete(region_id)
            if hasattr(self.repository, 'cache'):
                self.repository.cache.delete(f"regions:{region_id}")
                self.repository.cache.delete("regions:*")
            return deleted
        except PyMongoError as e:
            logger.error(f"Failed to delete region {region_id}", exc_info=True)
            raise DatabaseError({
                "message": "Failed to delete region",
                "details": {"error": str(e)}
            })

    def query_regions(self,
                    field_queries: Optional[dict] = None,
                    skip: int = 0,
                    limit: int = 100) -> List[Region]:
        """Query regions with flexible filters and pagination"""
        try:
            skip = max(0, skip)
            limit = min(100, max(1, limit))
            return self.repository.query_regions(field_queries, skip, limit)
        except PyMongoError as e:
            logger.error("Failed to query regions", exc_info=True)
            raise DatabaseError({
                "message": "Failed to query regions",
                "details": {"error": str(e)}
            })

    def get_region_by_name(self, name: str) -> Optional[Region]:
        """Get a region by its name"""
        try:
            return self.repository.get_by_name(name)
        except PyMongoError as e:
            logger.error(f"Failed to get region by name {name}", exc_info=True)
            raise DatabaseError({
                "message": "Failed to get region by name",
                "details": {"error": str(e)}
            })

    def search_regions(self, query: str, skip: int = 0, limit: int = 100) -> List[Region]:
        """Search regions by name or description"""
        try:
            skip = max(0, skip)
            limit = min(100, max(1, limit))
            results = self.repository.collection.find(
                {"$text": {"$search": query}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})])
            return [Region(**doc) for doc in results[skip:skip+limit]]
        except PyMongoError as e:
            logger.error(f"Failed to search regions with query {query}", exc_info=True)
            raise DatabaseError({
                "message": "Failed to search regions",
                "details": {"error": str(e)}
            })
