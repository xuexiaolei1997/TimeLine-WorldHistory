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
    """获取所有历史时期(前端兼容格式)
    Returns:
        Dict[str, Dict[str, str]]: 键为时期ID，值为包含以下字段的字典:
           - name: 时期名称(优先返回中文)
           - color: 时期颜色代码
    Notes:
        1. 使用Redis缓存结果(5分钟TTL)
        2. 自动转换多语言名称(优先返回中文)
        3. 结果按时期起始年份排序
    Examples:
        GET /periods/
        Response:
        {
            "507f1f77bcf86cd799439011": {
                "name": "中世纪",
                "color": "#FF5733"
            },
            "507f1f77bcf86cd799439012": {
                "name": "文艺复兴",
                "color": "#33FF57"
            }
        }
    """
    logger.info("获取所有历史时期列表(已转换为前端兼容格式)")
    periods = service.query_periods()
    return {p.periodId: transform_period(p) for p in periods}

@router.post("/", response_model=Period)
@handle_app_exceptions
async def create_period(
    period: PeriodCreate,
    service: PeriodService = Depends(get_period_service)
):
    """创建新历史时期(带字段验证)
    Args:
        period: 时期创建数据模型(包含以下字段):
           - name: 多语言名称(中英文必填其一)
           - description: 多语言描述(可选)
           - start_year: 起始年份(整数)
           - end_year: 结束年份(必须大于等于起始年份)
           - color: 颜色代码(十六进制格式)
    Returns:
        Period: 创建的历史时期对象(包含完整信息)
    Notes:
        1. 自动设置创建时间
        2. 创建成功后清除时期列表缓存
        3. 字段验证规则:
           - 名称至少提供一种语言
           - 结束年份必须大于等于起始年份
           - 颜色代码必须为有效的十六进制格式
    Examples:
        POST /periods/
        {
            "name": {"zh": "中世纪", "en": "Middle Ages"},
            "start_year": 476,
            "end_year": 1453,
            "color": "#FF5733"
        }
    """
    logger.info(f"创建新历史时期: {period.name.zh or period.name.en} (年份范围: {period.start_year}-{period.end_year}, 颜色: {period.color})")
    return service.create(period)

@router.post("/search", response_model=List[Period])
@cache_response(ttl=60)
async def search_periods(
    query: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: PeriodService = Depends(get_period_service)
):
    """全文搜索历史时期(名称和描述)
    Args:
        query: 搜索关键词(至少1个字符)
        skip: 跳过记录数(分页用)
        limit: 返回记录数(最大100)
    Returns:
        List[Period]: 匹配的历史时期列表(按匹配度排序)
    Notes:
        1. 使用Redis缓存结果(1分钟TTL)
        2. 支持中英文混合搜索
        3. 搜索算法:
           - 名称匹配权重高于描述
           - 中文关键词优先匹配中文字段
           - 英文关键词优先匹配英文字段
           - 支持部分匹配(包含关系)
    Examples:
        /search?query=罗马
        /search?query=roman&limit=5
    """
    logger.info(f"全文搜索历史时期 - 关键词: {query}, 分页: skip={skip}, limit={limit}")
    return service.search(query, skip=skip, limit=limit)

@router.get("/by-name/{name}", response_model=Optional[Period])
@cache_response(ttl=300)
@handle_app_exceptions
async def read_period_by_name(
    name: str,
    service: PeriodService = Depends(get_period_service)
):
    """按名称精确查询历史时期(完全匹配)
    Args:
        name: 时期名称(需完全匹配)
    Returns:
        Optional[Period]: 匹配的历史时期对象，未找到则返回None
    Notes:
        1. 使用Redis缓存结果(5分钟TTL)
        2. 名称区分大小写
        3. 仅返回完全匹配的结果
        4. 如需模糊匹配请使用/search端点
    Examples:
        /by-name/中世纪
        /by-name/Ancient%20Rome
    """
    logger.info(f"按名称精确查询历史时期: {name} (完全匹配模式)")
    return service.get_by_name(name)

@router.get("/by-year/{year}", response_model=List[Period])
@cache_response(ttl=300)
@handle_app_exceptions
async def read_periods_by_year(
    year: int,
    service: PeriodService = Depends(get_period_service)
):
    """按年份查询历史时期(基于起止年份范围)
    Args:
        year: 年份(整数)
    Returns:
        List[Period]: 包含该年份的历史时期列表(按起始年份排序)
    Notes:
        1. 使用Redis缓存结果(5分钟TTL)
        2. 返回所有包含该年份的时期(基于起止年份范围)
        3. 包含边界条件:
           - 包含起始年份等于该年份的时期
           - 包含结束年份等于该年份的时期
           - 包含该年份在起止年份之间的时期
    Examples:
        /by-year/1066 (查询1066年所属的历史时期)
        /by-year/-300 (查询公元前300年所属的历史时期)
    """
    logger.info(f"按年份范围查询历史时期: {year} (包含起止年份检查)")
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
    """灵活查询历史时期(支持多条件组合)
    Args:
        skip: 跳过记录数(分页用)
        limit: 返回记录数(最大100)
        **field_queries: 任意字段查询条件(支持以下字段):
            - name: 时期名称(模糊匹配)
            - description: 描述(模糊匹配)
            - start_year: 起始年份
            - end_year: 结束年份
            - color: 颜色代码
    Returns:
        List[Period]: 匹配的历史时期列表
    Notes:
        1. 使用Redis缓存结果(1分钟TTL)
        2. 支持任意字段组合查询
        3. 字符串字段支持模糊匹配(不区分大小写)
        4. 数值字段支持精确匹配
    Examples:
        /query?name=roman&limit=10
        /query?description=帝国&start_year=100
        /query?start_year=100&end_year=500&skip=20&limit=50
    """
    # 过滤掉None值和特殊参数
    field_queries = {
        k: v for k, v in field_queries.items() 
        if v is not None and k not in ['skip', 'limit']
    }
    
    logger.info(f"灵活查询历史时期 - 查询条件: {field_queries}, 分页: skip={skip}, limit={limit}")
    
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
    """按ID查询历史时期详情
    Args:
        period_id: 时期ID(MongoDB ObjectId)
    Returns:
        Period: 完整的历史时期对象，包含:
           - 多语言名称和描述
           - 起止年份
           - 颜色代码
           - 相关事件数量
           - 创建/更新时间
    Notes:
        1. 使用Redis缓存结果(5分钟TTL)
        2. 如果找不到会返回404错误
        3. 包含该时期的完整元数据
    Examples:
        /periods/507f1f77bcf86cd799439011
    """
    logger.info(f"按ID查询历史时期详情: {period_id}")
    return service.get(period_id)

@router.put("/{period_id}", response_model=Period)
@handle_app_exceptions
async def update_period(
    period_id: str,
    period: PeriodUpdate,
    service: PeriodService = Depends(get_period_service)
):
    """更新历史时期信息
    Args:
        period_id: 时期ID(MongoDB ObjectId)
        period: 时期更新数据模型(包含需要更新的字段)
    Returns:
        Period: 更新后的历史时期对象(包含完整信息)
    Notes:
        1. 自动更新最后修改时间
        2. 更新成功后清除相关缓存:
           - 该时期的单独缓存
           - 时期列表缓存
           - 如果时期名称变更: 清除旧名称缓存
           - 如果年份范围变更: 清除相关年份查询缓存
        3. 支持部分更新(仅更新提供的字段)
    Examples:
        - 更新名称: {"name": {"zh": "新名称"}}
        - 更新年份: {"start_year": -500, "end_year": 500}
    """
    logger.info(f"更新历史时期信息 - ID: {period_id} (更新字段: {period.dict(exclude_unset=True)})")
    return service.update(period_id, period)

@router.delete("/{period_id}")
@handle_app_exceptions
async def delete_period(
    period_id: str,
    service: PeriodService = Depends(get_period_service)
):
    """删除历史时期及其关联数据
    Args:
        period_id: 时期ID(MongoDB ObjectId)
    Returns:
        dict: 包含成功消息的字典
    Notes:
        1. 删除成功后清除相关缓存:
           - 该时期的单独缓存
           - 时期列表缓存
           - 所有包含该时期的查询缓存
        2. 同时处理关联数据:
           - 将该时期从所有关联事件中移除
           - 更新相关事件的缓存
        3. 操作不可逆，请谨慎使用
    Examples:
        DELETE /periods/507f1f77bcf86cd799439011
    """
    logger.info(f"删除历史时期及其关联数据 - ID: {period_id}")
    service.delete(period_id)
    return {"message": "历史时期删除成功"}
