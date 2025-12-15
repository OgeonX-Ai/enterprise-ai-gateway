from typing import List
from pydantic import BaseModel


class ServiceProvider(BaseModel):
    id: str
    display_name: str
    capabilities: List[str]
    supported: List[str]
    requires_auth: bool = False
    status: str = "enabled"
