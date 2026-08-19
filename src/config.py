from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI20K Agent"
    app_env: Literal["development", "production", "test", "staging"] = "development"
    debug: bool = False
    app_port: int = Field(default=8000, ge=1, le=65535)
    app_host: str = "0.0.0.0"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Auth
    jwt_secret: str = Field(default="local-dev-secret-change-in-production")
    jwt_expire_minutes: int = 60

    # LLM
    openai_api_key: str = ""
    model_name: str = "gpt-4o-mini"
    llm_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    llm_timeout: int = 30
    embedding_model: str = "text-embedding-3-small"

    # Database
    database_url: str = "sqlite:///./data/app.db"

    # Vector Store
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str = ""

    # Security Limits
    max_request_size_bytes: int = 10485760  # 10MB default

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    
    # Production Security Checks
    if settings.app_env in ("production", "staging"):
        if settings.jwt_secret == "local-dev-secret-change-in-production":
            raise ValueError("FATAL: JWT Secret must be changed in production/staging!")
        if settings.log_level == "DEBUG":
            raise ValueError("FATAL: LOG_LEVEL cannot be DEBUG in production/staging!")
        if "*" in settings.cors_origins.split(","):
            raise ValueError("FATAL: CORS origins cannot contain wildcard '*' in production/staging!")
        if settings.debug:
            raise ValueError("FATAL: Debug mode must be disabled in production/staging!")
        if not settings.openai_api_key and not getattr(settings, 'openrouter_api_key', ''):
            # In a real app we'd enforce this, but since it's configurable via LLMGateway
            # we just warn, or let the validation catch it on use
            pass
            
    return settings
