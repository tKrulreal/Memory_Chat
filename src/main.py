from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from src.api.routes import router
from src.api.v1.auth import router as auth_router
from src.api.v1.connections import router as connections_router
from src.api.v1.connection_requests import router as connection_requests_router
from src.api.v1.conversations import router as conversations_router
from src.api.v1.copilot import router as copilot_router
from src.api.v1.messages import router as messages_router
from src.api.v1.notifications import router as notifications_router
from src.api.v1.profile import router as profile_router
from src.api.v1.search import router as search_router

from src.api.ws import router as websocket_router
from src.config import get_settings
from src.core.exceptions import setup_exception_handlers
from src.core.logging import setup_logging, get_logger, set_request_id
from src.core.middlewares import RequestLoggingMiddleware
from src.events.bus import EventBus
from src.models.database import engine
from src.workers.memory_worker import MemoryWorker
from src.workers.connection_worker import ConnectionRecommendationWorker

# Initialize structured logging
settings = get_settings()
setup_logging(log_level=os.getenv("LOG_LEVEL", settings.log_level))
logger = get_logger(__name__)

APP_VERSION = "1.0.0-mvp"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("app_starting", app_name=settings.app_name, env=settings.app_env)

    app.state.event_bus = EventBus()

    # Start Outbox Worker
    from src.workers.outbox_worker import OutboxWorker
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    app.state.outbox_worker = OutboxWorker(
        event_bus=app.state.event_bus,
        session_factory=session_factory,
    )
    app.state.outbox_worker.start()
    logger.info("outbox_worker_started")

    # Start Memory Worker
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    app.state.memory_worker = MemoryWorker(
        event_bus=app.state.event_bus,
        session_factory=session_factory,
    )
    app.state.memory_worker.subscribe()
    logger.info("memory_worker_started")

    # Start Connection Recommendation Worker
    app.state.connection_worker = ConnectionRecommendationWorker(
        event_bus=app.state.event_bus,
    )
    app.state.connection_worker.subscribe()
    logger.info("connection_recommendation_worker_started")

    # Start APScheduler
    from src.core.scheduler import setup_scheduler, scheduler
    setup_scheduler(app)

    try:
        yield
    finally:
        logger.info("stopping_scheduler")
        scheduler.shutdown()
        logger.info("stopping_outbox_worker")
        if getattr(app.state, "outbox_worker", None):
            await app.state.outbox_worker.stop()
        logger.info("app_shutdown_complete")


from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from src.core.security_middlewares import RequestSizeLimitMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request

app = FastAPI(
    title="MemoryChat API",
    description="AI-powered P2P messaging",
    version=APP_VERSION,
    lifespan=lifespan,
)

# Set up Rate Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Rate Limit Exceeded", "message": f"Rate limit exceeded: {exc.detail}"}
    )

setup_exception_handlers(app)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    RequestSizeLimitMiddleware,
    max_request_size=settings.max_request_size_bytes,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from src.api.v1.settings import router as settings_router
from src.api.v1.tags import router as tags_router

app.include_router(router, prefix="/api/v1")
app.include_router(websocket_router)
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(conversations_router, prefix="/api/v1/direct-conversations", tags=["direct_conversations"])
app.include_router(messages_router, prefix="/api/v1", tags=["messages"])
app.include_router(notifications_router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(copilot_router, prefix="/api/v1/copilot", tags=["copilot"])
app.include_router(search_router, prefix="/api/v1/search", tags=["search"])
app.include_router(connections_router, prefix="/api/v1", tags=["connections"])
app.include_router(connection_requests_router, prefix="/api/v1", tags=["connection_requests"])
app.include_router(profile_router, prefix="/api/v1", tags=["profile"])
app.include_router(settings_router, prefix="/api/v1", tags=["settings"])
app.include_router(tags_router, prefix="/api/v1", tags=["tags"])


from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)

@app.get("/health/liveness", tags=["health"])
async def liveness():
    """
    Liveness probe for container orchestration.
    """
    return {"status": "ok", "version": APP_VERSION}

@app.get("/health/readiness", tags=["health"])
async def readiness():
    """
    Readiness probe. Checks if dependencies (like DB) are healthy.
    """
    db_status = "ok"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"
        logger.error("health_check_db_failed", error=str(e))
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Service Unavailable: DB connection failed")

    return {
        "status": "ok",
        "version": APP_VERSION,
        "db": db_status,
    }
