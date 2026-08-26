"""
Request Logging Middleware with Request ID tracking.
"""

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.logging import get_logger, set_request_id

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that:
    1. Generates a unique request ID for each request
    2. Logs request start and completion
    3. Adds request ID to response headers for tracing
    """

    async def dispatch(self, request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        set_request_id(request_id)

        # Add request ID to state for access in routes
        request.state.request_id = request_id

        # Record start time
        start_time = time.time()

        # Log request start
        logger.info(
            "request_start",
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown",
            request_id=request_id,
        )

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error and re-raise
            process_time = (time.time() - start_time) * 1000
            logger.error(
                "request_error",
                method=request.method,
                path=request.url.path,
                error=str(e),
                process_time_ms=round(process_time, 2),
                request_id=request_id,
            )
            raise

        # Calculate processing time
        process_time = (time.time() - start_time) * 1000

        # Log request completion
        log_level = "info" if response.status_code < 400 else "warning"
        log_func = logger.info if response.status_code < 400 else logger.warning

        log_func(
            "request_complete",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time_ms=round(process_time, 2),
            request_id=request_id,
        )

        # Add request ID to response headers for client tracing
        response.headers["X-Request-ID"] = request_id

        return response
