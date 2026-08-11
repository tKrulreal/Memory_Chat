import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

class NotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message

class UnauthorizedError(Exception):
    def __init__(self, message: str):
        self.message = message

def setup_exception_handlers(app):
    @app.exception_handler(NotFoundError)
    async def not_found_exception_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=404,
            content={"error": "Not Found", "message": exc.message},
        )

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_exception_handler(request: Request, exc: UnauthorizedError):
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized", "message": exc.message},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": "HTTP Error", "message": str(exc.detail)},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"error": "Validation Error", "details": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "message": "An unexpected error occurred."},
        )
