from typing import List, Dict, Any
from pymongo.database import Database
from core.repository import BaseRepository

class PeriodRepository(BaseRepository[Dict[str, Any]]):
    def __init__(self, db: Database):
        super().__init__("periods", db)

    def get_by_name(self, name: str) -> Dict[str, Any]:
        return self.collection.find_one({"name": name})

    def get_by_year_range(self, year: int) -> List[Dict[str, Any]]:
        return list(self.collection.find({
            "start_year": {"$lte": year},
            "end_year": {"$gte": year}
        }))
