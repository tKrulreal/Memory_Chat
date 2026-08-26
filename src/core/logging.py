"""
Structured Logging Configuration for MemoryChat.

Provides JSON logging for production with:
- Request ID tracking
- Structured JSON output
- AI prompt/response logging to separate files
- Log level configuration from environment
"""

import json
import logging
import os
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import structlog

# Context variable for request ID
request_id_var: ContextVar[str] = ContextVar("request_id", default="")

# AI log directory
AI_LOG_DIR = Path(os.getenv("AI_LOG_DIR", ".ai-log"))
AI_LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_request_id() -> str:
    """Get current request ID from context."""
    return request_id_var.get()


def set_request_id(request_id: str | None = None) -> str:
    """Set request ID in context. Generates one if not provided."""
    rid = request_id or str(uuid.uuid4())
    request_id_var.set(rid)
    return rid


class RequestIDFilter(logging.Filter):
    """Add request_id to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


class AIJsonHandler:
    """Handler that writes AI prompts/responses to JSON Lines files."""

    def __init__(self, log_dir: Path = AI_LOG_DIR):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _get_log_file(self) -> Path:
        """Get today's log file path."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self.log_dir / f"ai-{today}.jsonl"

    def log_ai_interaction(
        self,
        agent: str,
        prompt: str,
        response: str,
        model: str | None = None,
        tokens_used: int | None = None,
        latency_ms: float | None = None,
        error: str | None = None,
    ) -> None:
        """Log an AI interaction to JSON Lines file."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": get_request_id(),
            "agent": agent,
            "prompt": prompt,
            "response": response,
            "model": model,
            "tokens_used": tokens_used,
            "latency_ms": latency_ms,
            "error": error,
        }

        try:
            with open(self._get_log_file(), "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            # Don't let logging failures crash the app
            pass


# Global AI logger instance
ai_logger = AIJsonHandler()


def log_ai(
    agent: str,
    prompt: str,
    response: str,
    **kwargs,
) -> None:
    """Convenience function to log AI interactions."""
    ai_logger.log_ai_interaction(agent, prompt, response, **kwargs)


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure structured logging for the application.

    Sets up:
    - Console: Human-readable in development
    - File: JSON structured for production
    - Request ID tracking
    """

    # Determine if we're in production
    is_production = os.getenv("APP_ENV", "development") == "production"

    # Shared processors
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if is_production:
        # Production: JSON output
        shared_processors.append(structlog.processors.format_exc_info)
        renderer = structlog.processors.JSONRenderer()
    else:
        # Development: Colored console output
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    # Add request ID rendering
    def add_request_id_processor(logger, method_name, event_dict):
        event_dict["request_id"] = get_request_id()
        return event_dict

    shared_processors.append(add_request_id_processor)

    # Configure structlog
    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    handlers: list[logging.Handler] = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    handlers.append(console_handler)

    # File handler (JSON in production)
    log_file = AI_LOG_DIR / "app.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.addFilter(RequestIDFilter())
    handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
        handlers=handlers,
        force=True,
    )

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
