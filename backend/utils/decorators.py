from functools import wraps
from fastapi import HTTPException
from core.exceptions import AppExceptionCase, ValidationError
from typing import Any, Dict, Optional
from pydantic import ValidationError as PydanticValidationError
import inspect

def handle_app_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AppExceptionCase as e:
            raise HTTPException(status_code=e.status_code, detail=e.context)
        except PydanticValidationError as e:
            raise ValidationError({
                "message": "Validation error",
                "details": e.errors()
            })
    return wrapper

def wrap_response(success: bool = True, data: Optional[Any] = None, error: Optional[Dict] = None):
    response = {
        "success": success
    }
    if data is not None:
        response["data"] = data
    if error is not None:
        response["error"] = error
    return response
