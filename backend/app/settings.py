from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = Field("Enterprise AI Gateway", description="Application name")
    environment: str = Field("local", description="Deployment environment name")
    debug: bool = Field(True, description="Enable debug mode")
    correlation_id_header: str = Field("X-Correlation-ID", description="Header used for correlation IDs")
    default_channel: str = Field("web", description="Default channel for requests")

    model_config = {
        "env_prefix": "GATEWAY_",
        "env_file": ".env",
        "extra": "ignore",
    }


@lru_cache

def get_settings() -> Settings:
    return Settings()
