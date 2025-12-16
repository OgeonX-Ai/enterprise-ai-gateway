"""Local Whisper transcription helper built for demo use.

This module intentionally keeps everything CPU-only and manages lazy-loaded
Whisper models so the playground can spin up without heavy upfront costs.
"""

from __future__ import annotations

import datetime as dt
import io
import json
import time
from typing import Any, Dict, List, Tuple

import numpy as np
import soundfile as sf
import soxr
from faster_whisper import WhisperModel


DEFAULT_SETTINGS = {
    "model": "small",
    "compute_type": "int8",
    "language": None,
    "beam_size": 1,
    "chunk_length": 4,
    "vad_filter": True,
}

_MODEL_CACHE: Dict[Tuple[str, str], WhisperModel] = {}


def _timestamp() -> str:
    return dt.datetime.now().strftime("%H:%M:%S")


def _load_model(model_name: str, compute_type: str, logs: List[str]) -> WhisperModel:
    cache_key = (model_name, compute_type)
    if cache_key in _MODEL_CACHE:
        return _MODEL_CACHE[cache_key]

    logs.append(
        f"[{_timestamp()}] Loading model '{model_name}' on CPU (compute_type={compute_type})"
    )
    model = WhisperModel(model_name, device="cpu", compute_type=compute_type)
    _MODEL_CACHE[cache_key] = model
    logs.append(f"[{_timestamp()}] Model ready")
    return model


def _decode_audio(audio_bytes: bytes, logs: List[str]) -> Tuple[np.ndarray, int, float, float]:
    """Decode audio bytes and return mono 16k PCM array.

    Returns tuple of (audio_array, sample_rate, decode_ms, resample_ms).
    """

    decode_start = time.perf_counter()
    with io.BytesIO(audio_bytes) as buffer:
        audio_array, sample_rate = sf.read(buffer, always_2d=False)
    decode_ms = (time.perf_counter() - decode_start) * 1000

    if audio_array.ndim > 1:
        audio_array = np.mean(audio_array, axis=1)

    resample_ms = 0.0
    if sample_rate != 16000:
        resample_start = time.perf_counter()
        audio_array = soxr.resample(audio_array, sample_rate, 16000)
        resample_ms = (time.perf_counter() - resample_start) * 1000
        sample_rate = 16000
        logs.append(
            f"[{_timestamp()}] Resampled audio to 16 kHz mono (took {resample_ms:.1f} ms)"
        )

    return audio_array.astype(np.float32), sample_rate, decode_ms, resample_ms


def transcribe_audio(audio_bytes: bytes, raw_settings: Dict[str, Any]) -> Dict[str, Any]:
    """Transcribe audio bytes using faster-whisper with timing details."""

    logs: List[str] = []
    settings = {**DEFAULT_SETTINGS, **{k: v for k, v in raw_settings.items() if v is not None}}
    logs.append(
        "[{}] Config: model={} beam={} lang={} vad={} chunk={}s".format(
            _timestamp(),
            settings.get("model"),
            settings.get("beam_size"),
            settings.get("language") or "auto",
            settings.get("vad_filter"),
            settings.get("chunk_length"),
        )
    )

    total_start = time.perf_counter()
    audio_array, sample_rate, decode_ms, resample_ms = _decode_audio(audio_bytes, logs)
    audio_seconds = float(len(audio_array) / sample_rate)
    logs.append(f"[{_timestamp()}] Audio decoded ({audio_seconds:.2f}s)")

    model = _load_model(settings["model"], settings["compute_type"], logs)

    transcribe_start = time.perf_counter()
    segments, _ = model.transcribe(
        audio_array,
        language=settings.get("language") or None,
        beam_size=int(settings.get("beam_size", 1)),
        vad_filter=bool(settings.get("vad_filter", True)),
        chunk_length=int(settings.get("chunk_length", 4)),
    )
    transcribe_ms = (time.perf_counter() - transcribe_start) * 1000

    collected_segments: List[Dict[str, Any]] = []
    for segment in segments:
        collected_segments.append(
            {"start": float(segment.start), "end": float(segment.end), "text": segment.text}
        )

    text = " ".join([segment["text"].strip() for segment in collected_segments]).strip()
    total_ms = (time.perf_counter() - total_start) * 1000

    logs.append(f"[{_timestamp()}] thinking...")
    logs.append(f"[{_timestamp()}] RESULT ({audio_seconds:.2f}s audio in {transcribe_ms:.1f} ms)")
    logs.append(f"[{_timestamp()}] {text}")

    return {
        "text": text,
        "segments": collected_segments,
        "timing": {
            "audio_seconds": audio_seconds,
            "decode_ms": decode_ms,
            "resample_ms": resample_ms,
            "transcribe_ms": transcribe_ms,
            "total_ms": total_ms,
        },
        "logs": logs,
        "settings_used": settings,
    }


def parse_settings(settings_str: str | None) -> Dict[str, Any]:
    if not settings_str:
        return {}
    try:
        parsed = json.loads(settings_str)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}
