from fastapi import APIRouter, Depends, Request

from ..models import RegistryResponse, ValidationResponse
from ..runtime.agent_runtime import AgentRuntime

router = APIRouter(prefix="/v1")


def get_runtime(request: Request) -> AgentRuntime:
    return request.app.state.runtime


@router.get("/registry", response_model=RegistryResponse)
async def registry(request: Request, runtime: AgentRuntime = Depends(get_runtime)) -> RegistryResponse:
    include_unconfigured = request.app.state.settings.dev_mode
    snapshot = runtime.registry_snapshot()
    if not include_unconfigured:
        snapshot = {k: [item for item in v if item.get("configured")] for k, v in snapshot.items()}
    return RegistryResponse(**snapshot)


@router.get("/admin/config/validate", response_model=ValidationResponse)
async def validate(runtime: AgentRuntime = Depends(get_runtime)) -> ValidationResponse:
    return await runtime.validate_connectors()
