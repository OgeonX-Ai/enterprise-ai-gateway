from fastapi import APIRouter, Depends, Request

from ..runtime.agent_runtime import AgentRuntime
from ..models import RegistryResponse

router = APIRouter(prefix="/v1")


def get_runtime(request: Request) -> AgentRuntime:
    return request.app.state.runtime


@router.get("/registry", response_model=RegistryResponse)
async def registry(runtime: AgentRuntime = Depends(get_runtime)) -> RegistryResponse:
    snapshot = runtime.registry_snapshot()
    return RegistryResponse(**snapshot)
