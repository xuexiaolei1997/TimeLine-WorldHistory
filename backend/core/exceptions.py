from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette import status
from typing import Optional, Dict, Any

class AppExceptionCase(Exception):
    def __init__(self, 
                 status_code: int, 
                 context: Dict[str, Any], 
                 error_type: Optional[str] = None,
                 error_code: Optional[str] = None):
        self.exception_case = self.__class__.__name__
        self.status_code = status_code
        self.context = context
        self.error_type = error_type or "APPLICATION_ERROR"
        self.error_code = error_code

    def __str__(self):
        return (
            f"<AppException {self.exception_case} - "
            f"status_code={self.status_code} - "
            f"error_type={self.error_type} - "
            f"error_code={self.error_code} - "
            f"context={self.context}>"
        )

class DatabaseError(AppExceptionCase):
    def __init__(self, context: dict):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            context=context,
            error_type="DATABASE_ERROR"
        )

class ValidationError(AppExceptionCase):
    def __init__(self, context: dict):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            context=context,
            error_type="VALIDATION_ERROR"
        )

class NotFoundError(AppExceptionCase):
    def __init__(self, context: dict):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            context=context,
            error_type="NOT_FOUND"
        )

async def app_exception_handler(request: Request, exc: AppExceptionCase):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "type": exc.error_type,
                "code": exc.error_code,
                "message": exc.context.get("message", "An error occurred"),
                "details": exc.context.get("details", None)
            }
        },
    )

def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "type": "HTTP_ERROR",
                "message": exc.detail,
            }
        },
    )

def add_exception_handlers(app):
    app.add_exception_handler(AppExceptionCase, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
