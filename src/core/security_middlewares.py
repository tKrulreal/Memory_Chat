from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import status
import logging

logger = logging.getLogger(__name__)

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_request_size: int):
        super().__init__(app)
        self.max_request_size = max_request_size

    async def dispatch(self, request: Request, call_next):
        if request.headers.get("content-length"):
            try:
                content_length = int(request.headers["content-length"])
                if content_length > self.max_request_size:
                    logger.warning(
                        "Request blocked: Payload too large", 
                        extra={"content_length": content_length, "max_size": self.max_request_size}
                    )
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={"detail": "Payload too large"}
                    )
            except ValueError:
                pass
        
        return await call_next(request)
