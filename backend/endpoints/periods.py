from fastapi import APIRouter, Depends, Request, Query
from typing import List, Optional, Dict
import logging
from fastapi.logger import logger
from utils.cache import cache_response

from services.period_service import PeriodService
from core.dependencies import get_period_service
from schemas.period_schemas import PeriodCreate, Period, PeriodUpdate
from utils.decorators import handle_app_exceptions

router = APIRouter(prefix="/periods", tags=["periods"])

def transform_period(period: Period) -> Dict[str, str]:
    """Transform period data to match frontend expected format"""
    return {
        "name": period.name.zh or period.name.en,
        "color": period.color
    }

@router.get("/", response_model=Dict[str, Dict[str, str]])
@cache_response(ttl=300)
@handle_app_exceptions
async def list_periods(
    service: PeriodService = Depends(get_period_service)
):
    """Get all periods in frontend-compatible format"""
    logger.info("Fetching all periods")
    periods = service.query_periods()
    return {p.periodId: transform_period(p) for p in periods}

@router.post("/", response_model=Period)
@handle_app_exceptions
async def create_period(
    period: PeriodCreate,
    service: PeriodService = Depends(get_period_service)
):
    """Create a new period"""
    logger.info(f"Creating new period: {period.name}")
    return service.create(period)

@router.post("/search", response_model=List[Period])
@cache_response(ttl=60)
async def search_periods(
    query: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: PeriodService = Depends(get_period_service)
):
    """Search periods by name or description"""
    logger.info(f"Searching periods for: {query}")
    return service.search(query, skip=skip, limit=limit)

@router.get("/by-name/{name}", response_model=Optional[Period])
@cache_response(ttl=300)
@handle_app_exceptions
async def read_period_by_name(
    name: str,
    service: PeriodService = Depends(get_period_service)
):
    """Get period by exact name match"""
    logger.info(f"Fetching period by name: {name}")
    return service.get_by_name(name)

@router.get("/by-year/{year}", response_model=List[Period])
@cache_response(ttl=300)
@handle_app_exceptions
async def read_periods_by_year(
    year: int,
    service: PeriodService = Depends(get_period_service)
):
    """Get periods that include the specified year"""
    logger.info(f"Fetching periods for year: {year}")
    return service.get_by_year_range(year)

@router.post("/query", response_model=List[Period])
@cache_response(ttl=60)
@handle_app_exceptions
async def query_periods(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: PeriodService = Depends(get_period_service),
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
    
    return service.query_periods(
        field_queries=field_queries,
        skip=skip,
        limit=limit
    )

@router.get("/{period_id}", response_model=Period)
@cache_response(ttl=300)
@handle_app_exceptions
async def read_period(
    period_id: str,
    service: PeriodService = Depends(get_period_service)
):
    """Get period by ID"""
    logger.info(f"Fetching period by ID: {period_id}")
    return service.get(period_id)

@router.put("/{period_id}", response_model=Period)
@handle_app_exceptions
async def update_period(
    period_id: str,
    period: PeriodUpdate,
    service: PeriodService = Depends(get_period_service)
):
    """Update an existing period"""
    logger.info(f"Updating period {period_id}")
    return service.update(period_id, period)

@router.delete("/{period_id}")
@handle_app_exceptions
async def delete_period(
    period_id: str,
    service: PeriodService = Depends(get_period_service)
):
    """Delete a period"""
    logger.info(f"Deleting period {period_id}")
    service.delete(period_id)
    return {"message": "Period deleted successfully"}
