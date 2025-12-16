from typing import Any, Dict

from fastapi import APIRouter, Request

from ..runtime.stats import StatsTracker
from ..settings import Settings

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
