from typing import List
from sqlalchemy.orm import Session
from models import Period
from core.repository import BaseRepository

class PeriodRepository(BaseRepository[Period]):
    def __init__(self, db: Session):
        super().__init__(Period, db)

    def get_by_name(self, name: str) -> Period:
        return self.db.query(self.model).filter(self.model.name == name).first()

    def get_by_year_range(self, year: int) -> List[Period]:
        return (
            self.db.query(self.model)
            .filter(self.model.start_year <= year, self.model.end_year >= year)
            .all()
        )
