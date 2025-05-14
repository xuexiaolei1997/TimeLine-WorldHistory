from fastapi import APIRouter, Depends, Query, Request
from typing import List, Optional
import logging
from fastapi.logger import logger
from utils.cache import cache_response

from services.region_service import RegionRepository
from schemas.region_schemas import RegionCreate, Region, RegionUpdate
from utils.database import get_db
from utils.decorators import handle_app_exceptions

router = APIRouter(prefix="/regions", tags=["regions"])

def get_region_repo(
    request: Request,
    db = Depends(get_db)
) -> RegionRepository:
    """Dependency for getting RegionRepository instance"""
    with db as database:
        repo = RegionRepository(database)
        repo.cache = request.app.state.cache
        return repo

@router.post("/create", response_model=Region)
@handle_app_exceptions
async def create_region(
    region: RegionCreate, 
    repo: RegionRepository = Depends(get_region_repo)
):
    """Create a new region"""
    logger.info(f"Creating new region: {region.name}")
    res = repo.create(region)
    return res


@router.get("/by-period/{period_id}", response_model=List[Region])
@cache_response(ttl=300)
@handle_app_exceptions
async def read_regions_by_period(
    period_id: str,
    repo: RegionRepository = Depends(get_region_repo)
):
    """Get regions by period ID"""
    logger.info(f"Fetching regions for period: {period_id}")
    return repo.get_by_period(period_id)

@router.post("/contains-point", response_model=List[Region])
@cache_response(ttl=300)
@handle_app_exceptions
async def find_regions_containing_point(
    coordinates: List[float],
    repo: RegionRepository = Depends(get_region_repo)
):
    """Find regions that contain the given point"""
    logger.info(f"Finding regions containing point: {coordinates}")
    return repo.find_within(coordinates)

@router.get("/{region_id}", response_model=Region)
@handle_app_exceptions
async def read_region(
    region_id: str,
    repo: RegionRepository = Depends(get_region_repo)
):
    """Get region by ID"""
    logger.info(f"Fetching region by ID: {region_id}")
    ret = repo.get(region_id)
    return ret

@router.put("/{region_id}", response_model=Region)
@handle_app_exceptions
async def update_region(
    region_id: str,
    region: RegionUpdate,
    repo: RegionRepository = Depends(get_region_repo)
):
    """Update an existing region"""
    logger.info(f"Updating region {region_id}")
    res = repo.update(region_id, region)
    return res

@router.delete("/{region_id}")
@handle_app_exceptions
async def delete_region(
    region_id: str,
    repo: RegionRepository = Depends(get_region_repo)
):
    """Delete a region"""
    logger.info(f"Deleting region {region_id}")
    repo.delete(region_id)
    return {"message": "Region deleted successfully"}
