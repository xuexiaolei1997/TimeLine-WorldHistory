from typing import TypeVar, Generic, List, Dict, Any
from pymongo.database import Database
from bson import ObjectId
from .exceptions import AppExceptionCase

ModelType = TypeVar("ModelType", bound=Dict[str, Any])

class RepositoryException(AppExceptionCase):
    def __init__(self, status_code: int, context: dict):
        super().__init__(status_code, context)

class BaseRepository(Generic[ModelType]):
    def __init__(self, collection_name: str, db: Database):
        self.collection = db[collection_name]

    def get(self, id: str) -> ModelType:
        obj = self.collection.find_one({"_id": ObjectId(id)})
        if not obj:
            raise RepositoryException(
                status_code=404,
                context={"message": f"Document not found"}
            )
        return obj

    def list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return list(self.collection.find().skip(skip).limit(limit))

    def create(self, obj_in: dict) -> ModelType:
        try:
            result = self.collection.insert_one(obj_in)
            return self.get(str(result.inserted_id))
        except Exception as e:
            raise RepositoryException(
                status_code=400,
                context={"message": str(e)}
            )

    def update(self, id: str, obj_in: dict) -> ModelType:
        try:
            self.collection.update_one(
                {"_id": ObjectId(id)},
                {"$set": obj_in}
            )
            updated = self.get(id)
            
            # Clear relevant caches
            if hasattr(self, 'cache'):
                self.cache.delete(f"{self.collection.name}:*")
                self.cache.delete(f"{self.collection.name}:{id}")
                
            return updated
        except Exception as e:
            raise RepositoryException(
                status_code=400,
                context={"message": str(e)}
            )

    def delete(self, id: str) -> None:
        try:
            result = self.collection.delete_one({"_id": ObjectId(id)})
            if result.deleted_count == 0:
                raise RepositoryException(
                    status_code=404,
                    context={"message": "Document not found"}
                )
            
            # Clear relevant caches
            if hasattr(self, 'cache'):
                self.cache.delete(f"{self.collection.name}:*")
                self.cache.delete(f"{self.collection.name}:{id}")
                
        except Exception as e:
            raise RepositoryException(
                status_code=400,
                context={"message": str(e)}
            )
