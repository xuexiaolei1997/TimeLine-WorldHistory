from typing import Optional, Any
import redis
import json
from functools import wraps
from fastapi import Request, Depends
import logging
from fastapi.logger import logger
from pydantic import BaseModel
from datetime import timedelta
from core.exceptions import DatabaseError
import inspect

logger = logging.getLogger(__name__)

def get_cache(request: Request) -> 'CacheManager':
    """Dependency to get cache instance from app state"""
    return request.app.state.cache

class CacheConfig(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    retry_on_timeout: bool = True
    default_ttl: int = 300  # 5 minutes

class CacheManager:
    def __init__(self, config: CacheConfig):
        self.config = config
        self._fallback_cache = {}
        try:
            self.client = redis.Redis(
                host=config.host,
                port=config.port,
                db=config.db,
                password=config.password,
                socket_timeout=config.socket_timeout,
                socket_connect_timeout=config.socket_connect_timeout,
                retry_on_timeout=config.retry_on_timeout,
                decode_responses=True
            )
            # Test connection
            self.client.ping()
            self._using_redis = True
        except redis.RedisError as e:
            logger.warning("Cache initialization failed - using in-memory fallback", exc_info=True)
            self._using_redis = False

    def get(self, key: str) -> Any:
        if self._using_redis:
            try:
                data = self.client.get(key)
                return json.loads(data) if data else None
            except redis.RedisError as e:
                logger.warning(f"Redis get failed for key {key} - using fallback", exc_info=True)
                self._using_redis = False
            except json.JSONDecodeError as e:
                logger.error(f"Cache data corruption for key {key}", exc_info=True)
                self.delete(key)
                return None
        return self._fallback_cache.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        if self._using_redis:
            try:
                ttl = ttl if ttl is not None else self.config.default_ttl
                return bool(self.client.set(
                    key,
                    json.dumps(value),
                    ex=timedelta(seconds=ttl)
                ))
            except redis.RedisError as e:
                logger.warning(f"Redis set failed for key {key} - using fallback", exc_info=True)
                self._using_redis = False
        
        self._fallback_cache[key] = value
        return True

    def delete(self, key: str) -> bool:
        if self._using_redis:
            try:
                return bool(self.client.delete(key))
            except redis.RedisError as e:
                logger.warning(f"Redis delete failed for key {key} - using fallback", exc_info=True)
                self._using_redis = False
        
        if key in self._fallback_cache:
            del self._fallback_cache[key]
            return True
        return False

    def clear(self) -> bool:
        if self._using_redis:
            try:
                self.client.flushdb()
                return True
            except redis.RedisError as e:
                logger.warning("Redis clear failed - using fallback", exc_info=True)
                self._using_redis = False
        
        self._fallback_cache.clear()
        return True

    def close(self):
        try:
            self.client.close()
        except redis.RedisError as e:
            logger.error("Error closing cache connection", exc_info=True)

    def exists(self, key: str) -> bool:
        if self._using_redis:
            try:
                return bool(self.client.exists(key))
            except redis.RedisError as e:
                logger.warning(f"Redis exists check failed for key {key} - using fallback", exc_info=True)
                self._using_redis = False
        return key in self._fallback_cache

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        try:
            return self.client.incrby(key, amount)
        except redis.RedisError as e:
            logger.error(f"Cache increment failed for key {key}", exc_info=True)
            return None

    def health_check(self) -> bool:
        try:
            return bool(self.client.ping())
        except redis.RedisError:
            return False

def cache_response(ttl: int = 300):
    def decorator(func):
        # Preserve the original function's signature for FastAPI
        signature = inspect.signature(func)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request object from args or kwargs
            request = next((arg for arg in args if isinstance(arg, Request)), 
                         kwargs.get('request'))
            
            if not request or not isinstance(request, Request):
                return await func(*args, **kwargs)
            
            cache: CacheManager = request.app.state.cache
            cache_key = f"{request.url.path}?{request.url.query}"
            
            # Try to get cached response
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached
                
            # Call original function if cache miss
            response = await func(*args, **kwargs)
            
            # Cache the response
            cache.set(cache_key, response, ttl=ttl)
            logger.debug(f"Cached response for {cache_key}")
            
            return response
            
        # Copy the original signature parameters to the wrapper
        wrapper.__signature__ = signature
        return wrapper
    return decorator
