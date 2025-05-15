from fastapi import Request, HTTPException
import time
from collections import defaultdict
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, rate: int = 1000, burst: int = 2000):  # 显著提高限制
        self.rate = rate
        self.burst = burst
        self.requests: Dict[str, list] = defaultdict(list)
        self.window = 60

    def _clean_old_requests(self, ip: str):
        current = time.time()
        if ip in self.requests:
            self.requests[ip] = [ts for ts in self.requests[ip] 
                               if current - ts < self.window]

    def check_rate_limit(self, ip: str) -> Tuple[bool, float]:
        try:
            current = time.time()
            self._clean_old_requests(ip)
            
            request_count = len(self.requests[ip])
            
            # 简化判断逻辑
            if request_count >= self.burst:
                wait_time = self.window - (current - self.requests[ip][0])
                return False, max(0, wait_time)
                
            self.requests[ip].append(current)
            return True, 0
        except Exception as e:
            logger.warning(f"Rate limit check failed for IP {ip}: {str(e)}")
            return True, 0  # 出错时默认允许请求通过

limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    try:
        client_ip = request.client.host if request.client else "unknown"
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
        
        response = await call_next(request)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rate limit middleware error: {str(e)}")
        return await call_next(request)  # 出错时让请求通过