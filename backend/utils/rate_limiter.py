from fastapi import Request, HTTPException
from typing import Optional, Dict, Tuple
import time
from collections import defaultdict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class RequestLimit:
    """Request limit configuration"""
    max_requests: int
    window_seconds: int

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, default_limit: RequestLimit):
        self.default_limit = default_limit
        self.path_limits: Dict[str, RequestLimit] = {}
        self.requests: Dict[str, Dict[str, float]] = defaultdict(dict)
        
    def add_path_limit(self, path: str, limit: RequestLimit):
        """Add a specific rate limit for a path"""
        self.path_limits[path] = limit
        
    def _get_limit(self, path: str) -> RequestLimit:
        """Get the rate limit for a path"""
        return self.path_limits.get(path, self.default_limit)
        
    def _clean_old_requests(self, client_id: str, path: str, window: int):
        """Remove requests outside the current time window"""
        current = time.time()
        self.requests[client_id] = {
            ts: t for ts, t in self.requests[client_id].items()
            if current - t < window
        }
        
    def is_allowed(self, client_id: str, path: str) -> Tuple[bool, Optional[int]]:
        """Check if a request is allowed"""
        current = time.time()
        limit = self._get_limit(path)
        
        self._clean_old_requests(client_id, path, limit.window_seconds)
        
        # Count requests in current window
        client_requests = self.requests[client_id]
        request_count = len(client_requests)
        
        if request_count >= limit.max_requests:
            # Get oldest request time
            oldest_request = min(client_requests.values()) if client_requests else current
            retry_after = int(oldest_request + limit.window_seconds - current)
            return False, max(0, retry_after)
            
        # Record new request
        self.requests[client_id][str(current)] = current
        return True, None

# Create global rate limiter instance
rate_limiter = RateLimiter(
    default_limit=RequestLimit(max_requests=100, window_seconds=60)  # 100 requests per minute by default
)

# Add specific limits for different endpoints
rate_limiter.add_path_limit(
    "/events",
    RequestLimit(max_requests=50, window_seconds=60)  # 50 requests per minute for events
)
rate_limiter.add_path_limit(
    "/events/search",
    RequestLimit(max_requests=20, window_seconds=60)  # 20 searches per minute
)

async def rate_limit_middleware(request: Request, call_next):
    """FastAPI middleware for rate limiting"""
    # Get client identifier (IP address or API key)
    client_id = request.headers.get("X-API-Key") or request.client.host
    path = request.url.path
    
    # Check rate limit
    allowed, retry_after = rate_limiter.is_allowed(client_id, path)
    
    if not allowed:
        logger.warning(f"Rate limit exceeded for client {client_id} on path {path}")
        raise HTTPException(
            status_code=429,
            detail={
                "message": "Too many requests",
                "retry_after": retry_after
            }
        )
    
    return await call_next(request)