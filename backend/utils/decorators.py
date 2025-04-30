from functools import wraps
from fastapi import HTTPException
from core.exceptions import AppExceptionCase

def handle_app_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AppExceptionCase as e:
            raise HTTPException(status_code=e.status_code, detail=e.context)
    return wrapper
