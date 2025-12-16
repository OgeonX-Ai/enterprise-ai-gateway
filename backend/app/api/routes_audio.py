import base64
import json
import time
from typing import Any, Dict

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status

from ..runtime.agent_runtime import AgentRuntime
from ..runtime.stats import StatsTracker

router = APIRouter(prefix="/v1/audio")


def get_runtime(request: Request) -> AgentRuntime:
    return request.app.state.runtime


def get_stats(request: Request) -> StatsTracker:
    return request.app.state.stats_tracker


@router.post("/transcribe")
async def transcribe(
    request: Request,
    runtime: AgentRuntime = Depends(get_runtime),
    stats: StatsTracker = Depends(get_stats),
) -> dict:
    started = time.perf_counter()
    error: Exception | None = None
    try:
        body = await request.json()
        provider_id = body.get("stt_provider", "mock-stt")
        locale = body.get("locale", "en-US")
        model = body.get("model", "default")
        audio_bytes = base64.b64decode(body.get("audio_base64", "")) if body.get("audio_base64") else b""
        transcript = await runtime.transcribe_audio(provider_id, audio_bytes, locale=locale, model=model)
        return transcript
    except Exception as exc:  # noqa: BLE001
        error = exc
        raise
    finally:
        stats.record((time.perf_counter() - started) * 1000, error)


def _parse_transcribe_settings(settings_str: str | None) -> Dict[str, Any]:
    defaults: Dict[str, Any] = {
        "provider": "mock-stt",
        "language": "en-US",
        "model": "default",
        "beam_size": 1,
        "vad_filter": False,
        "temperature": 0.0,
    }

    if not settings_str:
        return defaults

    try:
        parsed = json.loads(settings_str)
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive guard
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid settings JSON: {exc}",
        ) from exc

    if not isinstance(parsed, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Settings must be a JSON object",
        )

    clean_settings = defaults | {key: parsed[key] for key in parsed if key in defaults}
    return clean_settings


@router.post("/transcribe-file")
async def transcribe_file(
    request: Request,
    file: UploadFile = File(...),
    settings: str | None = Form(None),
    runtime: AgentRuntime = Depends(get_runtime),
    stats: StatsTracker = Depends(get_stats),
) -> Dict[str, Any]:
    supported_types = {
        "audio/wav",
        "audio/wave",
        "audio/x-wav",
        "audio/webm",
        "audio/ogg",
    }

    if file.content_type and file.content_type not in supported_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported audio type {file.content_type}; please upload WAV or WEBM/OGG",
        )

    if file.content_type in {"audio/webm", "audio/ogg"}:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                "Opus/webm uploads require conversion; please send WAV/PCM at 16 kHz instead"
            ),
        )

    overall_start = time.perf_counter()
    error: Exception | None = None
    try:
        audio_bytes = await file.read()
        if not audio_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty audio file uploaded",
            )

        parse_started = time.perf_counter()
        parsed_settings = _parse_transcribe_settings(settings)
        locale = parsed_settings.get("language") or "en-US"
        provider_id = parsed_settings.get("provider", "mock-stt")
        model = parsed_settings.get("model", "default")

        decoding_ms = (time.perf_counter() - parse_started) * 1000

        transcribe_start = time.perf_counter()
        transcript = await runtime.transcribe_audio(provider_id, audio_bytes, locale=locale, model=model)
        transcribe_ms = (time.perf_counter() - transcribe_start) * 1000
    except Exception as exc:  # noqa: BLE001
        error = exc
        raise
    finally:
        total_ms = (time.perf_counter() - overall_start) * 1000
        stats.record(total_ms, error)

    transcript["settings_used"] = parsed_settings
    transcript["filename"] = file.filename
    transcript["timing"] = {
        "received_bytes": len(audio_bytes),
        "decode_ms": round(decoding_ms, 2),
        "transcribe_ms": round(transcribe_ms, 2),
        "total_ms": round(total_ms, 2),
        "audio_seconds": round(len(audio_bytes) / (16000 * 2), 2),
    }
    return transcript


@router.get("/transcribe-config")
async def transcribe_config() -> Dict[str, Any]:
    return {
        "models": ["tiny", "small", "medium"],
        "languages": ["fi", "en", "auto"],
        "beam_size": {"min": 1, "max": 5, "default": 1},
        "vad_filter": {"supported": True, "default": False},
        "notes": {
            "cpu_latency": "Medium model may run slowly on laptops; start with tiny/small for demos.",
        },
    }


@router.post("/synthesize")
async def synthesize(
    payload: dict,
    runtime: AgentRuntime = Depends(get_runtime),
) -> dict:
    provider_id = payload.get("tts_provider", "mock-tts")
    voice = payload.get("voice", "alloy")
    locale = payload.get("locale", "en-US")
    result = await runtime.synthesize_audio(provider_id, payload.get("text", ""), locale=locale, voice=voice)
    audio_base64 = base64.b64encode(result.get("audio", b"")) if result.get("audio") else b""
    return {"audio_base64": audio_base64.decode(), "latency_ms": result.get("latency_ms")}
