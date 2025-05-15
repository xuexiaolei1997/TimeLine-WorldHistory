from fastapi import APIRouter, Depends, Query, Request
from typing import List, Optional, Dict
import logging
from fastapi.logger import logger
from utils.cache import cache_response

from services.region_service import RegionService
from core.dependencies import get_region_service
from schemas.region_schemas import RegionCreate, Region, RegionUpdate
from utils.decorators import handle_app_exceptions

router = APIRouter(prefix="/regions", tags=["regions"])

def transform_region(region: Region) -> Dict:
    """Transform region data to match frontend expected format"""
    return {
        "id": str(region.id),
        "name": region.name.zh or region.name.en,
        "period": region.period_id,
        "boundary": {
            "type": region.boundary.type,
            "coordinates": region.boundary.coordinates
        },
        "color": region.color
    }

@router.get("/", response_model=List[Dict])
@cache_response(ttl=300)
@handle_app_exceptions
async def list_regions(
    service: RegionService = Depends(get_region_service)
):
    """Get all regions in frontend-compatible format"""
    logger.info("Fetching all regions")
    regions = service.query_regions()
    return [transform_region(region) for region in regions]

@router.post("/create", response_model=Region)
@handle_app_exceptions
async def create_region(
    region: RegionCreate, 
    service: RegionService = Depends(get_region_service)
):
    """Create a new region"""
    logger.info(f"Creating new region: {region.name}")
    res = service.create(region)
    return res


@router.get("/by-period/{period_id}", response_model=List[Region])
@cache_response(ttl=300)
@handle_app_exceptions
async def read_regions_by_period(
    period_id: str,
    service: RegionService = Depends(get_region_service)
):
    """Get regions by period ID"""
    logger.info(f"Fetching regions for period: {period_id}")
    return service.get_by_period(period_id)

@router.post("/contains-point", response_model=List[Region])
@cache_response(ttl=300)
@handle_app_exceptions
async def find_regions_containing_point(
    coordinates: List[float],
    service: RegionService = Depends(get_region_service)
):
    """Find regions that contain the given point"""
    logger.info(f"Finding regions containing point: {coordinates}")
    return service.find_within(coordinates)

@router.get("/{region_id}", response_model=Region)
@handle_app_exceptions
async def read_region(
    region_id: str,
    service: RegionService = Depends(get_region_service)
):
    """Get region by ID"""
    logger.info(f"Fetching region by ID: {region_id}")
    ret = service.get(region_id)
    return ret

@router.put("/{region_id}", response_model=Region)
@handle_app_exceptions
async def update_region(
    region_id: str,
    region: RegionUpdate,
    service: RegionService = Depends(get_region_service)
):
    """Update an existing region"""
    logger.info(f"Updating region {region_id}")
    res = service.update(region_id, region)
    return res

@router.delete("/{region_id}")
@handle_app_exceptions
async def delete_region(
    region_id: str,
    service: RegionService = Depends(get_region_service)
):
    """Delete a region"""
    logger.info(f"Deleting region {region_id}")
    service.delete(region_id)
    return {"message": "Region deleted successfully"}
