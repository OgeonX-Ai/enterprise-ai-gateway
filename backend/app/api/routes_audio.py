from __future__ import annotations

import base64
import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Tuple

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from fastapi.responses import JSONResponse

from ..common.logging import bind_correlation_id, get_logger
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
        raise ValueError(f"Invalid settings JSON: {exc}") from exc

    if not isinstance(parsed, dict):
        raise ValueError("Settings must be a JSON object")

    clean_settings = defaults | {key: parsed[key] for key in parsed if key in defaults}
    return clean_settings


def _guess_extension(content_type: str) -> str:
    if content_type == "audio/webm":
        return ".webm"
    if content_type == "audio/ogg":
        return ".ogg"
    if content_type in {"audio/wav", "audio/wave", "audio/x-wav"}:
        return ".wav"
    return ".bin"


def _convert_with_ffmpeg(audio_bytes: bytes, content_type: str) -> Tuple[bytes, float]:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is required to convert audio/webm or audio/ogg. Please install ffmpeg.")

    convert_start = time.perf_counter()
    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = Path(tmpdir) / f"input{_guess_extension(content_type)}"
        output_path = Path(tmpdir) / "output.wav"
        input_path.write_bytes(audio_bytes)

        process = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(input_path),
                "-ac",
                "1",
                "-ar",
                "16000",
                "-f",
                "wav",
                str(output_path),
            ],
            capture_output=True,
            check=False,
        )

        if process.returncode != 0:
            stderr = process.stderr.decode("utf-8", errors="ignore")
            raise RuntimeError(f"FFmpeg conversion failed ({process.returncode}): {stderr.strip()[:500]}")

        wav_bytes = output_path.read_bytes()

    convert_ms = (time.perf_counter() - convert_start) * 1000
    return wav_bytes, convert_ms


async def _ensure_wav(audio_bytes: bytes, content_type: str, logger) -> Tuple[bytes, float, str]:
    safe_content_type = content_type or "application/octet-stream"
    if safe_content_type in {"audio/wav", "audio/wave", "audio/x-wav"}:
        logger.info("Using uploaded WAV audio without conversion", extra={"bytes": len(audio_bytes)})
        return audio_bytes, 0.0, "wav"

    if safe_content_type in {"audio/webm", "audio/ogg"}:
        wav_bytes, convert_ms = _convert_with_ffmpeg(audio_bytes, safe_content_type)
        logger.info(
            "Converted audio to WAV for Whisper",
            extra={"bytes_in": len(audio_bytes), "bytes_out": len(wav_bytes), "convert_ms": round(convert_ms, 2)},
        )
        return wav_bytes, convert_ms, "wav"

    raise ValueError(
        f"Unsupported format {safe_content_type}. Supported: audio/wav, audio/webm, audio/ogg (conversion)."
    )


@router.post("/transcribe-file")
async def transcribe_file(
    request: Request,
    file: UploadFile = File(...),
    settings: str | None = Form(None),
    runtime: AgentRuntime = Depends(get_runtime),
    stats: StatsTracker = Depends(get_stats),
) -> Dict[str, Any]:
    logger = bind_correlation_id(
        get_logger(__name__), request.headers.get(request.app.state.settings.correlation_id_header)
    )

    overall_start = time.perf_counter()
    error: Exception | None = None
    response_data: Dict[str, Any] = {}
    status_code = status.HTTP_200_OK

    try:
        raw_bytes = await file.read()
        if not raw_bytes:
            status_code = status.HTTP_400_BAD_REQUEST
            raise ValueError("Empty audio file uploaded")

        logger.info(
            "Received audio upload",
            extra={
                "filename": file.filename,
                "content_type": file.content_type or "unknown",
                "bytes": len(raw_bytes),
            },
        )

        parsed_settings = _parse_transcribe_settings(settings)
        locale = parsed_settings.get("language") or "en-US"
        provider_id = parsed_settings.get("provider", "mock-stt")
        model = parsed_settings.get("model", "default")

        decode_start = time.perf_counter()
        try:
            wav_bytes, convert_ms, fmt = await _ensure_wav(raw_bytes, file.content_type or "", logger)
        except RuntimeError as exc:  # explicit conversion errors
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            raise exc
        decoding_ms = (time.perf_counter() - decode_start) * 1000

        transcribe_start = time.perf_counter()
        logger.info(
            "Starting transcription", extra={"provider": provider_id, "model": model, "locale": locale}
        )
        transcript = await runtime.transcribe_audio(provider_id, wav_bytes, locale=locale, model=model)
        transcribe_ms = (time.perf_counter() - transcribe_start) * 1000

        total_ms = (time.perf_counter() - overall_start) * 1000
        logger.info(
            "Transcription completed",
            extra={
                "text_preview": (transcript.get("text", "") or "")[:120],
                "total_ms": round(total_ms, 2),
                "transcribe_ms": round(transcribe_ms, 2),
            },
        )

        response_data = {
            "text": transcript.get("text", ""),
            "timing": {
                "total_ms": round(total_ms, 2),
                "transcribe_ms": round(transcribe_ms, 2),
                "convert_ms": round(convert_ms, 2),
                "decode_ms": round(decoding_ms, 2),
                "audio_seconds": round(len(wav_bytes) / (16000 * 2), 2),
            },
            "settings_used": parsed_settings,
            "filename": file.filename,
            "format": fmt,
        }
    except ValueError as exc:
        error = exc
        status_code = status.HTTP_400_BAD_REQUEST
        logger.warning("Transcription request rejected", extra={"reason": str(exc)})
        response_data = {"error": str(exc)}
    except RuntimeError as exc:
        error = exc
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        logger.error("Audio conversion failed", extra={"reason": str(exc)})
        response_data = {"error": str(exc)}
    except Exception as exc:  # noqa: BLE001
        error = exc
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        logger.exception("Unhandled error during transcription")
        response_data = {"error": str(exc)}
    finally:
        total_elapsed = (time.perf_counter() - overall_start) * 1000
        stats.record(total_elapsed, error)

    return JSONResponse(status_code=status_code, content=response_data)


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
