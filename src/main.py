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

    try:
        yield
    finally:
        logger.info("stopping_outbox_worker")
        if getattr(app.state, "outbox_worker", None):
            await app.state.outbox_worker.stop()
        logger.info("app_shutdown_complete")


app = FastAPI(
    title="MemoryChat API",
    description="AI-powered P2P messaging",
    version=APP_VERSION,
    lifespan=lifespan,
)

setup_exception_handlers(app)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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



@app.get("/health")
async def health():
    """
    Health check endpoint.

    Returns:
        - status: "ok" if healthy
        - version: Application version
        - db: Database connection status
    """
    db_status = "ok"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"
        logger.error("health_check_db_failed", error=str(e))

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "version": APP_VERSION,
        "db": db_status,
    }
