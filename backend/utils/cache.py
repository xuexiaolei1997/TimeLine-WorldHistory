from typing import Optional, Any
import redis
import json
from functools import wraps
from fastapi import Request
import logging
from fastapi.logger import logger
from pydantic import BaseModel
from datetime import timedelta
from core.exceptions import DatabaseError

logger = logging.getLogger(__name__)

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
        try:
            self.config = config
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
        except redis.RedisError as e:
            logger.error("Cache initialization failed", exc_info=True)
            raise DatabaseError({
                "message": "Failed to initialize cache connection",
                "details": {"error": str(e)}
            })

    def get(self, key: str) -> Any:
        try:
            data = self.client.get(key)
            return json.loads(data) if data else None
        except redis.RedisError as e:
            logger.error(f"Cache get failed for key {key}", exc_info=True)
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Cache data corruption for key {key}", exc_info=True)
            self.delete(key)
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            ttl = ttl if ttl is not None else self.config.default_ttl
            return bool(self.client.set(
                key,
                json.dumps(value),
                ex=timedelta(seconds=ttl)
            ))
        except redis.RedisError as e:
            logger.error(f"Cache set failed for key {key}", exc_info=True)
            return False
        except (TypeError, json.JSONEncodeError) as e:
            logger.error(f"Cache serialization failed for key {key}", exc_info=True)
            return False

    def delete(self, key: str) -> bool:
        try:
            return bool(self.client.delete(key))
        except redis.RedisError as e:
            logger.error(f"Cache delete failed for key {key}", exc_info=True)
            return False

    def clear(self) -> bool:
        try:
            self.client.flushdb()
            return True
        except redis.RedisError as e:
            logger.error("Cache clear failed", exc_info=True)
            return False

    def close(self):
        try:
            self.client.close()
        except redis.RedisError as e:
            logger.error("Error closing cache connection", exc_info=True)

    def exists(self, key: str) -> bool:
        try:
            return bool(self.client.exists(key))
        except redis.RedisError as e:
            logger.error(f"Cache exists check failed for key {key}", exc_info=True)
            return False

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
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            cache: CacheManager = request.app.state.cache
            cache_key = f"{request.url.path}?{request.url.query}"
            
            # Try to get cached response
            cached = cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached
                
            # Call original function if cache miss
            response = await func(request, *args, **kwargs)
            
            # Cache the response
            cache.set(cache_key, response, ttl=ttl)
            logger.debug(f"Cached response for {cache_key}")
            
            return response
        return wrapper
    return decorator
