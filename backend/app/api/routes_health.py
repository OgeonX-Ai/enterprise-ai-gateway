import platform
import sys
from datetime import datetime, timezone

from fastapi import APIRouter, Request

from ..settings import Settings, get_settings

router = APIRouter()
_started_at = datetime.now(timezone.utc)


@router.get("/healthz")
async def healthcheck(request: Request) -> dict:
    settings: Settings = getattr(request.app.state, "settings", get_settings())
    uptime_seconds = int((datetime.now(timezone.utc) - _started_at).total_seconds())

    return {
        "status": "ok",
        "app": {
            "name": settings.app_name,
            "version": settings.app_version,
            "commit": settings.build_sha or "",
            "environment": settings.environment,
        },
        "runtime": {
            "stt_provider": settings.stt_provider,
            "default_model": settings.stt_default_model,
            "default_language": settings.stt_default_language,
            "hardware_hint": settings.hardware_hint,
            "python": sys.version,
            "platform": platform.platform(),
        },
        "uptime": {
            "started_at": _started_at.isoformat(),
            "seconds": uptime_seconds,
        },
        "debug": {"stream_enabled": settings.enable_debug_stream},
    }
