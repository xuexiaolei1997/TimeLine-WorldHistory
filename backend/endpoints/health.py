from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from typing import Dict, List
import psutil
import time
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from utils.performance_logger import get_performance_metrics
from utils.database import get_db
from utils.check_mongo import check_mongo_connection
from utils.performance import performance_monitor
from core.exceptions import DatabaseError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["health"])

def get_system_metrics() -> Dict:
    """获取系统资源使用情况"""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent
    }

@router.get("")
async def health_check(db = Depends(get_db)):
    """健康检查端点"""
    try:
        # 检查数据库连接
        db.command("ping")
        db_status = "healthy"
    except Exception as e:
        db_status = "unhealthy"

    # 获取系统指标
    system_metrics = get_system_metrics()
    
    # 获取API性能指标
    performance_data = get_performance_metrics()
    
    # 计算总体状态
    status = "healthy"
    if (system_metrics["cpu_percent"] > 90 or 
        system_metrics["memory_percent"] > 90 or 
        db_status == "unhealthy"):
        status = "unhealthy"
    
    return {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "system": system_metrics,
        "metrics": performance_data
    }

@router.get("/alerts")
async def get_alerts() -> List[Dict]:
    """获取性能警报"""
    alerts = []
    performance_data = get_performance_metrics()
    
    # 检查响应时间
    for endpoint, metrics in performance_data.items():
        if metrics["average_response_time"] > 1000:  # 超过1秒
            alerts.append({
                "severity": "warning",
                "endpoint": endpoint,
                "metric": "average_response_time",
                "value": f"{metrics['average_response_time']:.2f}ms",
                "threshold": "1000ms",
                "timestamp": datetime.now().isoformat()
            })
        
        if metrics["error_rate"] > 0.05:  # 错误率超过5%
            alerts.append({
                "severity": "error",
                "endpoint": endpoint,
                "metric": "error_rate",
                "value": f"{metrics['error_rate'] * 100:.1f}%",
                "threshold": "5%",
                "timestamp": datetime.now().isoformat()
            })
        
        if metrics["p95_response_time"] > 2000:  # P95超过2秒
            alerts.append({
                "severity": "warning",
                "endpoint": endpoint,
                "metric": "p95_response_time",
                "value": f"{metrics['p95_response_time']:.2f}ms",
                "threshold": "2000ms",
                "timestamp": datetime.now().isoformat()
            })
    
    # 检查系统资源
    system_metrics = get_system_metrics()
    
    if system_metrics["cpu_percent"] > 80:
        alerts.append({
            "severity": "warning",
            "endpoint": "system",
            "metric": "cpu_usage",
            "value": f"{system_metrics['cpu_percent']}%",
            "threshold": "80%",
            "timestamp": datetime.now().isoformat()
        })
    
    if system_metrics["memory_percent"] > 80:
        alerts.append({
            "severity": "warning",
            "endpoint": "system",
            "metric": "memory_usage",
            "value": f"{system_metrics['memory_percent']}%",
            "threshold": "80%",
            "timestamp": datetime.now().isoformat()
        })
    
    return alerts