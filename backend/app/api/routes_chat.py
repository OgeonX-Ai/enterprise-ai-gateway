import uuid

from fastapi import APIRouter, Depends, Request

from ..models import ChatRequest, ChatResponse, SessionResponse
from ..runtime.agent_runtime import AgentRuntime

router = APIRouter(prefix="/v1")


def get_runtime(request: Request) -> AgentRuntime:
    return request.app.state.runtime


@router.post("/sessions", response_model=SessionResponse)
async def create_session(runtime: AgentRuntime = Depends(get_runtime)) -> SessionResponse:
    session_id = str(uuid.uuid4())
    runtime.memory.create_session(session_id)
    return SessionResponse(session_id=session_id)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    request: Request,
    runtime: AgentRuntime = Depends(get_runtime),
) -> ChatResponse:
    correlation_header = request.app.state.settings.correlation_id_header
    correlation_id = request.headers.get(correlation_header)
    return await runtime.handle_chat(payload, correlation_id)
