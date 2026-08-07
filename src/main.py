from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker

from src.api.routes import router
from src.api.v1.auth import router as auth_router
from src.api.v1.contacts import router as contacts_router
from src.api.v1.conversations import router as conversations_router
from src.api.v1.copilot import router as copilot_router
from src.api.v1.memory import router as memory_router
from src.api.v1.messages import router as messages_router
from src.api.v1.recommendations import router as recommendations_router
from src.api.v1.search import router as search_router
from src.api.ws import router as websocket_router
from src.config import get_settings
from src.core.exceptions import setup_exception_handlers
from src.core.middlewares import RequestLoggingMiddleware
from src.events.bus import EventBus
from src.models.database import SessionLocal
from src.workers.memory_worker import MemoryWorker


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    print(f"Starting {settings.app_name} in {settings.app_env} mode")
    app.state.event_bus = EventBus()
    await app.state.event_bus.start()

    # Start Memory Worker
    from src.models.database import engine
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    app.state.memory_worker = MemoryWorker(
        event_bus=app.state.event_bus,
        session_factory=session_factory,
    )
    app.state.memory_worker.subscribe()
    print("MemoryWorker started")

    try:
        yield
    finally:
        # Drain EventBus queue before shutdown
        print("Draining EventBus...")
        await app.state.event_bus.join()
        await app.state.event_bus.stop()
        print("Shutting down...")


app = FastAPI(
    title="AI20K Agent",
    description="AI Agent built with LangGraph",
    version="1.0.0",
    lifespan=lifespan,
)

setup_exception_handlers(app)

settings = get_settings()
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
app.include_router(contacts_router, prefix="/api/v1/contacts", tags=["contacts"])
app.include_router(conversations_router, prefix="/api/v1/conversations", tags=["conversations"])
app.include_router(messages_router, prefix="/api/v1", tags=["messages"])
app.include_router(memory_router, prefix="/api/v1/memory", tags=["memory"])
app.include_router(recommendations_router, prefix="/api/v1/recommendations", tags=["recommendations"])
app.include_router(search_router, prefix="/api/v1/search", tags=["search"])
app.include_router(copilot_router, prefix="/api/v1/copilot", tags=["copilot"])


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.app_env}
