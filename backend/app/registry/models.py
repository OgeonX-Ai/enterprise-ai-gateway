from typing import List

from pydantic import BaseModel, Field


class ServiceProvider(BaseModel):
    id: str
    display_name: str
    capabilities: List[str]
    supported: List[str]
    requires_auth: bool = False
    status: str = "available"
    configured: bool = True
    missing_env: List[str] = Field(default_factory=list)
