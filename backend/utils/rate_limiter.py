from fastapi import Request, HTTPException
import time
from collections import defaultdict
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, rate: int = 100, burst: int = 200):
        """
        初始化速率限制器
        
        Args:
            rate: 每分钟允许的请求数
            burst: 突发请求的最大数量
        """
        self.rate = rate  # requests per minute
        self.burst = burst
        self.requests: Dict[str, list] = defaultdict(list)
        self.window = 60  # 1 minute window

    def _clean_old_requests(self, ip: str):
        """清理旧请求记录"""
        current = time.time()
        self.requests[ip] = [ts for ts in self.requests[ip] 
                           if current - ts < self.window]

    def check_rate_limit(self, ip: str) -> Tuple[bool, float]:
        """
        检查是否超过速率限制
        
        Args:
            ip: 客户端IP地址
            
        Returns:
            (是否允许请求, 需要等待的秒数)
        """
        current = time.time()
        self._clean_old_requests(ip)
        
        # 检查突发限制
        if len(self.requests[ip]) >= self.burst:
            wait_time = self.window - (current - self.requests[ip][0])
            return False, max(0, wait_time)
            
        # 检查速率限制
        request_count = len(self.requests[ip])
        if request_count >= self.rate:
            # 计算需要等待的时间
            wait_time = self.window - (current - self.requests[ip][0])
            return False, max(0, wait_time)
            
        # 记录请求
        self.requests[ip].append(current)
        return True, 0

# 创建全局实例
limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """FastAPI中间件，用于实现请求速率限制"""
    # 获取客户端IP
    client_ip = request.client.host if request.client else "unknown"
    
    # 检查速率限制
    allowed, wait_time = limiter.check_rate_limit(client_ip)
    
    if not allowed:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=429,
            detail={
                "error": "rate_limit_exceeded",
                "message": "Too many requests",
                "wait_time": wait_time
            }
        )
    
    # 继续处理请求
    response = await call_next(request)
    return response