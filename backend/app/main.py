import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .api import routes_admin, routes_audio, routes_chat, routes_health
from .common.logging import configure_logging
from .registry.service_registry import ServiceRegistry
from .runtime.agent_runtime import AgentRuntime
from .runtime.context_builder import ContextBuilder
from .runtime.memory_store import MemoryStore
from .runtime.policy import PolicyEngine
from .runtime.router import RuntimeRouter
from .settings import get_settings

configure_logging()
settings = get_settings()

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

runtime = AgentRuntime(
    registry=ServiceRegistry(),
    memory=MemoryStore(),
    context_builder=ContextBuilder(),
    policy_engine=PolicyEngine(),
    runtime_router=RuntimeRouter(),
)

app.state.runtime = runtime
app.state.settings = settings


@app.middleware("http")
async def ensure_correlation_id(request: Request, call_next):
    correlation_id = request.headers.get(settings.correlation_id_header) or str(uuid.uuid4())
    request.headers.__dict__["_list"].append(
        (settings.correlation_id_header.encode(), correlation_id.encode())
    )
    response = await call_next(request)
    response.headers[settings.correlation_id_header] = correlation_id
    return response


app.include_router(routes_health.router)
app.include_router(routes_admin.router)
app.include_router(routes_chat.router)
app.include_router(routes_audio.router)
