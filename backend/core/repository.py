from typing import Type, TypeVar, Generic, List
from sqlalchemy.orm import Session
from models import Base
from .exceptions import AppExceptionCase

ModelType = TypeVar("ModelType", bound=Base)

class RepositoryException(AppExceptionCase):
    def __init__(self, status_code: int, context: dict):
        super().__init__(status_code, context)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: int) -> ModelType:
        obj = self.db.query(self.model).filter(self.model.id == id).first()
        if not obj:
            raise RepositoryException(
                status_code=404,
                context={"message": f"{self.model.__name__} not found"}
            )
        return obj

    def list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj_in: dict) -> ModelType:
        try:
            db_obj = self.model(**obj_in)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except Exception as e:
            self.db.rollback()
            raise RepositoryException(
                status_code=400,
                context={"message": str(e)}
            )

    def update(self, id: int, obj_in: dict) -> ModelType:
        db_obj = self.get(id)
        try:
            for field in obj_in:
                setattr(db_obj, field, obj_in[field])
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except Exception as e:
            self.db.rollback()
            raise RepositoryException(
                status_code=400,
                context={"message": str(e)}
            )

    def delete(self, id: int) -> None:
        db_obj = self.get(id)
        try:
            self.db.delete(db_obj)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise RepositoryException(
                status_code=400,
                context={"message": str(e)}
            )
