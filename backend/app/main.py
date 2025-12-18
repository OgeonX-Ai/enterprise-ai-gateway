import uuid
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api import (
    routes_admin,
    routes_audio,
    routes_chat,
    routes_health,
    routes_runtime,
    routes_servicenow_tools,
    routes_whisper,
)
from .api.routes_debug import router as routes_debug
from .common.logging import configure_logging
from .registry.service_registry import ServiceRegistry
from .runtime.agent_runtime import AgentRuntime
from .runtime.context_builder import ContextBuilder
from .runtime.memory_store import MemoryStore
from .runtime.policy import PolicyEngine
from .runtime.router import RuntimeRouter
from .runtime.stats import StatsTracker
from .settings import get_settings
from .speech import SpeechRouter

log_broadcaster = configure_logging()
settings = get_settings()

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    # CORS enabled for local demo UI (GitHub Pages -> localhost)
    allow_origins=[origin.strip() for origin in settings.cors_allow_origins.split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

registry = ServiceRegistry(settings=settings)

runtime = AgentRuntime(
    settings=settings,
    registry=registry,
    memory=MemoryStore(),
    context_builder=ContextBuilder(),
    policy_engine=PolicyEngine(),
    runtime_router=RuntimeRouter(),
)

app.state.runtime = runtime
app.state.settings = settings
app.state.stats_tracker = StatsTracker()
app.state.log_stream = log_broadcaster
app.state.speech_router = SpeechRouter(settings)

static_whisper_dir = Path(__file__).parent / "static" / "whisper"
app.mount(
    "/tools/whisper",
    StaticFiles(directory=static_whisper_dir, html=True),
    name="whisper-tools",
)

static_whisper_dir = Path(__file__).parent / "static" / "whisper"
app.mount(
    "/tools/whisper",
    StaticFiles(directory=static_whisper_dir, html=True),
    name="whisper-tools",
)


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
app.include_router(routes_runtime.router)
app.include_router(routes_servicenow_tools.router)
app.include_router(routes_whisper.router)
app.include_router(routes_debug)
