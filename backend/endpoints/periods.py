from fastapi import APIRouter, Depends
from typing import List
from pymongo.database import Database

from services.period_service import PeriodRepository
from schemas.period_schemas import PeriodCreate, Period, PeriodUpdate
from utils.database import db_manager
from utils.decorators import handle_app_exceptions

router = APIRouter(prefix="/periods", tags=["periods"])

@router.post("/", response_model=Period)
@handle_app_exceptions
def create_period(period: PeriodCreate, db: Database = Depends(db_manager.get_db)):
    repo = PeriodRepository(db)
    return repo.create(period.dict())

@router.get("/", response_model=List[Period])
def read_periods(skip: int = 0, limit: int = 100, db: Database = Depends(db_manager.get_db)):
    repo = PeriodRepository(db)
    return repo.list(skip=skip, limit=limit)

@router.get("/{period_id}", response_model=Period)
@handle_app_exceptions
def read_period(period_id: str, db: Database = Depends(db_manager.get_db)):
    repo = PeriodRepository(db)
    return repo.get(period_id)

@router.put("/{period_id}", response_model=Period)
@handle_app_exceptions
def update_period(period_id: str, period: PeriodUpdate, db: Database = Depends(db_manager.get_db)):
    repo = PeriodRepository(db)
    return repo.update(period_id, period.dict(exclude_unset=True))

@router.delete("/{period_id}")
@handle_app_exceptions
def delete_period(period_id: str, db: Database = Depends(db_manager.get_db)):
    repo = PeriodRepository(db)
    repo.delete(period_id)
    return {"message": "Period deleted successfully"}
