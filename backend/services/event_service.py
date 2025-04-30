from typing import List
from sqlalchemy.orm import Session
from models import Event
from core.repository import BaseRepository

class EventRepository(BaseRepository[Event]):
    def __init__(self, db: Session):
        super().__init__(Event, db)

    def get_by_title(self, title: str) -> Event:
        return self.db.query(self.model).filter(self.model.title == title).first()

    def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Event]:
        return (
            self.db.query(self.model)
            .filter(self.model.title.contains(query) | self.model.description.contains(query))
            .offset(skip)
            .limit(limit)
            .all()
        )
