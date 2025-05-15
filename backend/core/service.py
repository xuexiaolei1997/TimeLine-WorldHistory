from typing import TypeVar, Generic, Optional, List
from pymongo.database import Database
from pymongo.errors import PyMongoError
import logging
from .exceptions import DatabaseError, NotFoundError
from .repository import BaseRepository

logger = logging.getLogger(__name__)
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType") 
UpdateSchemaType = TypeVar("UpdateSchemaType")

class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base service class providing common CRUD operations"""
    
    def __init__(self, repository: BaseRepository[ModelType]):
        self.repository = repository

    def get(self, id: str) -> ModelType:
        """Get single item by ID"""
        try:
            item = self.repository.get(id)
            if not item:
                raise NotFoundError({
                    "message": "Item not found",
                    "details": {"id": id}
                })
            return item
        except PyMongoError as e:
            logger.error(f"Failed to get item {id}", exc_info=True)
            raise DatabaseError({
                "message": "Failed to fetch item",
                "details": {"error": str(e)}
            })

    def list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """List items with pagination"""
        try:
            return self.repository.list(skip=skip, limit=limit)
        except PyMongoError as e:
            logger.error("Failed to list items", exc_info=True)
            raise DatabaseError({
                "message": "Failed to list items", 
                "details": {"error": str(e)}
            })

    def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create new item"""
        try:
            return self.repository.create(obj_in.dict())
        except PyMongoError as e:
            logger.error("Failed to create item", exc_info=True)
            raise DatabaseError({
                "message": "Failed to create item",
                "details": {"error": str(e)}
            })

    def update(self, id: str, obj_in: UpdateSchemaType) -> ModelType:
        """Update existing item"""
        try:
            return self.repository.update(id, obj_in.dict())
        except PyMongoError as e:
            logger.error(f"Failed to update item {id}", exc_info=True)
            raise DatabaseError({
                "message": "Failed to update item",
                "details": {"error": str(e)}
            })

    def delete(self, id: str) -> None:
        """Delete item by ID"""
        try:
            self.repository.delete(id)
        except PyMongoError as e:
            logger.error(f"Failed to delete item {id}", exc_info=True)
            raise DatabaseError({
                "message": "Failed to delete item",
                "details": {"error": str(e)}
            })
