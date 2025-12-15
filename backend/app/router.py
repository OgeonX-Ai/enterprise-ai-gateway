from typing import Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .memory import MemoryStore
from .registry import ConnectorRegistry


class RouteRequest(BaseModel):
    session_id: str = Field(..., description="Session identifier for memory tracking")
    target: str = Field(..., description="Connector to route the message to")
    message: str = Field(..., description="User message to process")


class RouteResponse(BaseModel):
    target: str
    response: str
    trace_id: str
    memory: Dict[str, List[Dict[str, str]]]


class ConnectorListResponse(BaseModel):
    connectors: List[str]


def create_router(memory: MemoryStore, registry: ConnectorRegistry) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @router.get("/connectors", response_model=ConnectorListResponse)
    def list_connectors() -> ConnectorListResponse:
        return ConnectorListResponse(connectors=list(registry.list()))

    @router.post("/route", response_model=RouteResponse)
    def route_request(payload: RouteRequest) -> RouteResponse:
        connector = registry.get(payload.target)
        if not connector:
            raise HTTPException(status_code=404, detail=f"Connector '{payload.target}' not found")

        # Persist user message
        memory.append(payload.session_id, "user", payload.message)

        # Execute connector
        result = connector.run(payload.message, payload.session_id)

        # Persist connector response
        memory.append(payload.session_id, payload.target, result.get("response", ""))

        history = memory.get_history(payload.session_id)
        return RouteResponse(**result, memory={"history": history})

    return router
