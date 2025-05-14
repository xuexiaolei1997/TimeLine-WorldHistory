from typing import TypeVar, Generic, List, Dict, Any
from pymongo.database import Database
from bson import ObjectId
from pymongo.errors import PyMongoError
from .exceptions import DatabaseError, NotFoundError, ValidationError
import logging

logger = logging.getLogger(__name__)
ModelType = TypeVar("ModelType", bound=Dict[str, Any])

class BaseRepository(Generic[ModelType]):
    def __init__(self, collection_name: str, db: Database):
        self.collection = db[collection_name]

    def get(self, id: str) -> ModelType:
        try:
            obj = self.collection.find_one({"_id": ObjectId(id)})
            if not obj:
                raise NotFoundError({
                    "message": "Document not found",
                    "details": {"id": id}
                })
            return obj
        except PyMongoError as e:
            logger.error(f"Database error in get(): {str(e)}", exc_info=True)
            raise DatabaseError({
                "message": "Failed to fetch document",
                "details": {"error": str(e)}
            })

    def list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        try:
            return list(self.collection.find().skip(skip).limit(limit))
        except PyMongoError as e:
            logger.error(f"Database error in list(): {str(e)}", exc_info=True)
            raise DatabaseError({
                "message": "Failed to list documents",
                "details": {"error": str(e)}
            })

    def create(self, obj_in: dict) -> ModelType:
        try:
            result = self.collection.insert_one(obj_in)
            return self.get(str(result.inserted_id))
        except PyMongoError as e:
            logger.error(f"Database error in create(): {str(e)}", exc_info=True)
            raise DatabaseError({
                "message": "Failed to create document",
                "details": {"error": str(e)}
            })

    def update(self, id: str, obj_in: dict) -> ModelType:
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(id)},
                {"$set": obj_in}
            )
            if result.matched_count == 0:
                raise NotFoundError({
                    "message": "Document not found",
                    "details": {"id": id}
                })
            
            updated = self.get(id)
            
            # Clear relevant caches
            if hasattr(self, 'cache'):
                self.cache.delete(f"{self.collection.name}:*")
                self.cache.delete(f"{self.collection.name}:{id}")
                
            return updated
        except PyMongoError as e:
            logger.error(f"Database error in update(): {str(e)}", exc_info=True)
            raise DatabaseError({
                "message": "Failed to update document",
                "details": {"error": str(e)}
            })

    def delete(self, id: str) -> None:
        try:
            result = self.collection.delete_one({"_id": ObjectId(id)})
            if result.deleted_count == 0:
                raise NotFoundError({
                    "message": "Document not found",
                    "details": {"id": id}
                })
            
            # Clear relevant caches
            if hasattr(self, 'cache'):
                self.cache.delete(f"{self.collection.name}:*")
                self.cache.delete(f"{self.collection.name}:{id}")
                
        except PyMongoError as e:
            logger.error(f"Database error in delete(): {str(e)}", exc_info=True)
            raise DatabaseError({
                "message": "Failed to delete document",
                "details": {"error": str(e)}
            })

    def exists(self, id: str) -> bool:
        try:
            return bool(self.collection.find_one({"_id": ObjectId(id)}, {"_id": 1}))
        except PyMongoError as e:
            logger.error(f"Database error in exists(): {str(e)}", exc_info=True)
            raise DatabaseError({
                "message": "Failed to check document existence",
                "details": {"error": str(e)}
            })
