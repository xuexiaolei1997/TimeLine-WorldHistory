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
    """获取所有地理区域列表(前端兼容格式)
    Returns:
        List[Dict]: 转换后的区域列表，包含:
           - id: 区域ID
           - name: 区域名称(优先返回中文)
           - period: 所属时期ID
           - boundary: 边界坐标信息
           - color: 区域颜色代码
    Notes:
        1. 使用Redis缓存结果(5分钟TTL)
        2. 自动转换多语言名称(优先返回中文)
        3. 边界坐标格式为GeoJSON标准
    Examples:
        GET /regions/
    """
    logger.info("获取所有地理区域列表(已转换为前端兼容格式)")
    regions = service.query_regions()
    return [transform_region(region) for region in regions]

@router.post("/create", response_model=Region)
@handle_app_exceptions
async def create_region(
    region: RegionCreate, 
    service: RegionService = Depends(get_region_service)
):
    """创建新地理区域(包含边界验证)
    Args:
        region: 区域创建数据模型(包含以下字段):
           - name: 多语言名称(中英文)
           - period_id: 所属时期ID
           - boundary: 边界坐标(GeoJSON格式)
           - color: 区域颜色代码
    Returns:
        Region: 创建的地理区域对象(包含完整信息)
    Notes:
        1. 自动设置创建时间
        2. 创建成功后清除区域列表缓存
        3. 边界验证规则:
           - 必须是有效的GeoJSON多边形
           - 坐标点必须形成闭合环
           - 不允许自相交
        4. 名称不能与现有区域重复
    Examples:
        POST /regions/create
        {
            "name": {"zh": "中原", "en": "Central Plains"},
            "period_id": "507f1f77bcf86cd799439011",
            "boundary": {
                "type": "Polygon",
                "coordinates": [[[x1,y1],[x2,y2],...]]
            },
            "color": "#FF0000"
        }
    """
    logger.info(f"创建新地理区域: {region.name.zh or region.name.en} (边界点数量: {len(region.boundary.coordinates[0])})")
    res = service.create(region)
    return res


@router.get("/by-period/{period_id}", response_model=List[Region])
@cache_response(ttl=300)
@handle_app_exceptions
async def read_regions_by_period(
    period_id: str,
    service: RegionService = Depends(get_region_service)
):
    """按时期ID查询关联地理区域(包含边界信息)
    Args:
        period_id: 时期ID(MongoDB ObjectId)
    Returns:
        List[Region]: 关联的地理区域列表，每个区域包含:
           - id: 区域ID
           - name: 区域名称
           - boundary: 边界坐标
           - color: 区域颜色
    Notes:
        1. 使用Redis缓存结果(5分钟TTL)
        2. 返回空列表表示该时期无关联区域
        3. 结果按区域名称排序
        4. 边界坐标格式为GeoJSON多边形
    Examples:
        GET /regions/by-period/507f1f77bcf86cd799439011
    """
    logger.info(f"查询时期关联地理区域 - 时期ID: {period_id}")
    return service.get_by_period(period_id)

@router.post("/contains-point", response_model=List[Region])
@cache_response(ttl=300)
@handle_app_exceptions
async def find_regions_containing_point(
    coordinates: List[float],
    service: RegionService = Depends(get_region_service)
):
    """查询包含指定坐标点的地理区域(地理空间查询)
    Args:
        coordinates: 坐标点[经度, 纬度](WGS84坐标系)
    Returns:
        List[Region]: 包含该点的地理区域列表(按区域面积升序排列)
    Notes:
        1. 使用Redis缓存结果(5分钟TTL)
        2. 坐标格式为[经度, 纬度](WGS84坐标系)
        3. 使用MongoDB地理空间索引加速查询
        4. 支持点与多边形包含关系计算
        5. 返回结果按区域面积升序排列(小区域优先)
    Examples:
        POST /regions/contains-point
        [116.404, 39.915]  # 北京天安门坐标
    """
    logger.info(f"地理空间查询 - 坐标点: {coordinates} (WGS84坐标系)")
    return service.find_within(coordinates)

@router.get("/{region_id}", response_model=Region)
@handle_app_exceptions
async def read_region(
    region_id: str,
    service: RegionService = Depends(get_region_service)
):
    """按ID查询地理区域详情(包含关联数据)
    Args:
        region_id: 区域ID(MongoDB ObjectId)
    Returns:
        Region: 地理区域详情对象，包含:
           - id: 区域ID
           - name: 多语言名称
           - period_id: 所属时期ID
           - boundary: 边界坐标(GeoJSON格式)
           - color: 区域颜色代码
           - event_count: 关联事件数量
           - created_at: 创建时间
           - last_updated: 最后更新时间
    Notes:
        1. 包含完整区域信息和关联数据
        2. 如果找不到会返回404错误
        3. 边界坐标格式为GeoJSON多边形
    Examples:
        GET /regions/507f1f77bcf86cd799439011
    """
    logger.info(f"查询地理区域详情 - ID: {region_id} (包含关联数据)")
    ret = service.get(region_id)
    return ret

@router.put("/{region_id}", response_model=Region)
@handle_app_exceptions
async def update_region(
    region_id: str,
    region: RegionUpdate,
    service: RegionService = Depends(get_region_service)
):
    """更新地理区域信息(包含边界验证)
    Args:
        region_id: 区域ID(MongoDB ObjectId)
        region: 区域更新数据模型(包含需要更新的字段)
    Returns:
        Region: 更新后的地理区域对象(包含完整信息)
    Notes:
        1. 自动更新最后修改时间
        2. 更新成功后清除相关缓存:
           - 该区域的单独缓存
           - 区域列表缓存
           - 如果区域名称变更: 清除旧名称缓存
           - 如果边界变更: 清除所有包含该区域的查询缓存
        3. 边界变更时会重新验证:
           - 必须是有效的GeoJSON多边形
           - 坐标点必须形成闭合环
           - 不允许自相交
    Examples:
        PUT /regions/507f1f77bcf86cd799439011
        {
            "name": {"zh": "新名称"},
            "boundary": {
                "type": "Polygon",
                "coordinates": [[[x1,y1],[x2,y2],...]]
            }
        }
    """
    logger.info(f"更新地理区域信息 - ID: {region_id} (更新字段: {region.dict(exclude_unset=True)})")
    res = service.update(region_id, region)
    return res

@router.delete("/{region_id}")
@handle_app_exceptions
async def delete_region(
    region_id: str,
    service: RegionService = Depends(get_region_service)
):
    """删除地理区域及其关联数据
    Args:
        region_id: 区域ID(MongoDB ObjectId)
    Returns:
        dict: 包含成功消息的字典
    Notes:
        1. 删除成功后清除相关缓存:
           - 该区域的单独缓存
           - 区域列表缓存
           - 所有包含该区域的查询缓存
        2. 同时处理关联数据:
           - 将该区域从所有关联事件中移除
           - 更新相关事件的缓存
        3. 操作不可逆，请谨慎使用
    Examples:
        DELETE /regions/507f1f77bcf86cd799439011
    """
    logger.info(f"删除地理区域及其关联数据 - ID: {region_id}")
    service.delete(region_id)
    return {"message": "地理区域删除成功"}
