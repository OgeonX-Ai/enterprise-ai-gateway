from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Request

from ..integrations.servicenow.config import ServiceNowConfig
from ..runtime.stats import StatsTracker
from ..settings import Settings
from ..speech import SpeechRouter

router = APIRouter()


def _runtime_meta(settings: Settings) -> Dict[str, Any]:
    return {
        "stt_provider": settings.stt_provider,
        "device": "cpu",
        "compute_type": "int8",
        "default_model": settings.stt_default_model,
        "default_language": settings.stt_default_language,
        "defaults": {"beam_size": 1, "vad_filter": True},
        "hardware_hint": settings.hardware_hint,
    }


@router.get("/v1/runtime")
async def runtime(request: Request) -> Dict[str, Any]:
    settings: Settings = request.app.state.settings
    stats: StatsTracker = request.app.state.stats_tracker

    snapshot = stats.snapshot()
    p50, p95 = stats.percentiles()

    return {
        "backend_ready": snapshot.backend_ready,
        "stt_ready": snapshot.stt_ready,
        "runtime": _runtime_meta(settings),
        "stats": {
            "since_started_at": snapshot.started_at.isoformat(),
            "total_requests": snapshot.total_requests,
            "total_failures": snapshot.total_failures,
            "last_request_at": snapshot.last_request_at.isoformat() if snapshot.last_request_at else None,
            "last_latency_ms": snapshot.last_latency_ms,
            "rolling_window_size": snapshot.latencies.maxlen,
            "p50_latency_ms": p50,
            "p95_latency_ms": p95,
            "last_error": snapshot.last_error,
        },
    }


@router.get("/v1/runtime/status")
async def runtime_status(request: Request) -> Dict[str, Any]:
    settings: Settings = request.app.state.settings
    stats: StatsTracker = request.app.state.stats_tracker
    speech_router: SpeechRouter = request.app.state.speech_router

    speech_status = speech_router.status()
    sn_mode = ServiceNowConfig.from_settings(settings).mode_label
    stats_snapshot = stats.snapshot()

    return {
        "backend_ok": True,
        "servicenow_mode": sn_mode,
        "stt_provider_active": speech_status.stt_provider_active,
        "stt_provider_mode": speech_status.mode,
        "stt_provider_used": speech_status.stt_provider_active,
        "elevenlabs_ok": speech_status.elevenlabs_ok,
        "last_error": speech_status.last_error or stats_snapshot.last_error,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
