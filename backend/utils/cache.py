from typing import Optional, Any
import redis
import json
from functools import wraps
from fastapi import Request
import logging
from fastapi.logger import logger
from pydantic import BaseModel
import pickle
from datetime import timedelta

class CacheConfig(BaseModel):
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    default_ttl: int = 300  # 5 minutes

class CacheManager:
    def __init__(self, config: CacheConfig):
        self.config = config
        self.client = redis.Redis(
            host=config.host,
            port=config.port,
            db=config.db,
            password=config.password,
            decode_responses=False
        )
        self.default_ttl = config.default_ttl

    def get(self, key: str) -> Optional[Any]:
        try:
            cached = self.client.get(key)
            if cached:
                return pickle.loads(cached)
            return None
        except redis.RedisError as e:
            logger.error(f"Cache get failed for key {key}", exc_info=True)
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            ttl = ttl if ttl is not None else self.default_ttl
            return self.client.set(
                key,
                pickle.dumps(value),
                ex=timedelta(seconds=ttl)
            )
        except redis.RedisError as e:
            logger.error(f"Cache set failed for key {key}", exc_info=True)
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
