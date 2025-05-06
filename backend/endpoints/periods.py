from fastapi import APIRouter, Depends, Request
from typing import List
from pymongo.database import Database

from services.period_service import PeriodRepository
from schemas.period_schemas import PeriodCreate, Period, PeriodUpdate
from utils.database import get_db
from utils.decorators import handle_app_exceptions

router = APIRouter(prefix="/periods", tags=["periods"])

def get_period_repo(
    request: Request,
    db = Depends(get_db)
) -> PeriodRepository:
    """Dependency for getting PeriodRepository instance"""
    with db as database:
        repo = PeriodRepository(database)
        return repo

@router.post("/", response_model=Period)
@handle_app_exceptions
async def create_period(
    period: PeriodCreate,
    repo: PeriodRepository = Depends(get_period_repo)
):
    return repo.create(period.dict())

@router.get("/", response_model=List[Period])
async def read_periods(
    skip: int = 0,
    limit: int = 100,
    repo: PeriodRepository = Depends(get_period_repo)
):
    return repo.list(skip=skip, limit=limit)

@router.get("/{period_id}", response_model=Period)
@handle_app_exceptions
async def read_period(
    period_id: str,
    repo: PeriodRepository = Depends(get_period_repo)
):
    return repo.get(period_id)

@router.put("/{period_id}", response_model=Period)
@handle_app_exceptions
async def update_period(
    period_id: str,
    period: PeriodUpdate,
    repo: PeriodRepository = Depends(get_period_repo)
):
    return repo.update(period_id, period.dict(exclude_unset=True))

@router.delete("/{period_id}")
@handle_app_exceptions
async def delete_period(
    period_id: str,
    repo: PeriodRepository = Depends(get_period_repo)
):
    repo.delete(period_id)
    return {"message": "Period deleted successfully"}
