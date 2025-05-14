from fastapi import APIRouter, Request
from utils.check_mongo import check_mongo_connection
from utils.performance import performance_monitor
from core.exceptions import DatabaseError
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check(request: Request):
    """Check the health of all backend services"""
    health_status = {
        "status": "healthy",
        "services": {}
    }

    # Check MongoDB
    try:
        mongo_healthy = check_mongo_connection()
        health_status["services"]["mongodb"] = {
            "status": "healthy" if mongo_healthy else "unhealthy"
        }
    except DatabaseError as e:
        health_status["status"] = "degraded"
        health_status["services"]["mongodb"] = {
            "status": "unhealthy",
            "error": e.context.get("message")
        }

    # Check Redis cache
    try:
        cache = request.app.state.cache
        cache_healthy = cache.health_check()
        health_status["services"]["redis"] = {
            "status": "healthy" if cache_healthy else "unhealthy"
        }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["services"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # Get performance alerts
    alerts = performance_monitor.get_alerts()
    if alerts:
        health_status["status"] = "degraded"
        health_status["alerts"] = alerts

    # Set overall status to unhealthy if any service is unhealthy
    if any(service["status"] == "unhealthy" 
           for service in health_status["services"].values()):
        health_status["status"] = "unhealthy"

    return health_status

@router.get("/metrics")
async def performance_metrics():
    """Get performance metrics for all endpoints"""
    return {
        "success": True,
        "data": performance_monitor.get_metrics()
    }

@router.get("/alerts")
async def performance_alerts():
    """Get current performance alerts"""
    return {
        "success": True,
        "data": performance_monitor.get_alerts()
    }