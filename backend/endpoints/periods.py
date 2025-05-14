from fastapi import APIRouter, Depends, Request, Query
from typing import List, Optional
import logging
from fastapi.logger import logger
from utils.cache import cache_response

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
        repo.cache = request.app.state.cache
        return repo

@router.post("/", response_model=Period)
@handle_app_exceptions
async def create_period(
    period: PeriodCreate,
    repo: PeriodRepository = Depends(get_period_repo)
):
    """Create a new period"""
    logger.info(f"Creating new period: {period.name}")
    return repo.create(period)

@router.post("/search", response_model=List[Period])
@cache_response(ttl=60)
async def search_periods(
    request: Request,
    query: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    repo: PeriodRepository = Depends(get_period_repo)
):
    """Search periods by name or description"""
    logger.info(f"Searching periods for: {query}")
    return repo.search(query, skip=skip, limit=limit)

@router.get("/by-name/{name}", response_model=Optional[Period])
@cache_response(ttl=300)
@handle_app_exceptions
async def read_period_by_name(
    name: str,
    repo: PeriodRepository = Depends(get_period_repo)
):
    """Get period by exact name match"""
    logger.info(f"Fetching period by name: {name}")
    return repo.get_by_name(name)

@router.get("/by-year/{year}", response_model=List[Period])
@cache_response(ttl=300)
@handle_app_exceptions
async def read_periods_by_year(
    year: int,
    repo: PeriodRepository = Depends(get_period_repo)
):
    """Get periods that include the specified year"""
    logger.info(f"Fetching periods for year: {year}")
    return repo.get_by_year_range(year)

@router.post("/query", response_model=List[Period])
@cache_response(ttl=60)
@handle_app_exceptions
async def query_periods(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    repo: PeriodRepository = Depends(get_period_repo),
    **field_queries: Optional[str]
):
    """
    Flexible query periods with:
    - Arbitrary field queries (fuzzy matching for strings)
    - Pagination
    
    Examples:
    - /query?name=roman
    - /query?description=empire
    - /query?start_year=100&end_year=500
    """
    # Filter out None values and special params
    field_queries = {
        k: v for k, v in field_queries.items() 
        if v is not None and k not in ['skip', 'limit']
    }
    
    logger.info(f"Querying periods with filters: {field_queries}")
    
    return repo.query_periods(
        field_queries=field_queries,
        skip=skip,
        limit=limit
    )

@router.get("/{period_id}", response_model=Period)
@cache_response(ttl=300)
@handle_app_exceptions
async def read_period(
    period_id: str,
    repo: PeriodRepository = Depends(get_period_repo)
):
    """Get period by ID"""
    logger.info(f"Fetching period by ID: {period_id}")
    return repo.get(period_id)

@router.put("/{period_id}", response_model=Period)
@handle_app_exceptions
async def update_period(
    period_id: str,
    period: PeriodUpdate,
    repo: PeriodRepository = Depends(get_period_repo)
):
    """Update an existing period"""
    logger.info(f"Updating period {period_id}")
    return repo.update(period_id, period)

@router.delete("/{period_id}")
@handle_app_exceptions
async def delete_period(
    period_id: str,
    repo: PeriodRepository = Depends(get_period_repo)
):
    """Delete a period"""
    logger.info(f"Deleting period {period_id}")
    repo.delete(period_id)
    return {"message": "Period deleted successfully"}
