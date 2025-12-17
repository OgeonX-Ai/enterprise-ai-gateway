from __future__ import annotations

import asyncio
import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

from faster_whisper import WhisperModel

from ...common.logging import get_logger, log_event
from ...settings import Settings
from .base import SpeechProvider, Stopwatch, TranscriptionOptions, TranscriptionResult


class LocalWhisperProvider(SpeechProvider):
    name = "local_whisper"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        self._model: Optional[WhisperModel] = None
        self._model_name = settings.stt_default_model
        self._compute_type = settings.stt_whisper_compute_type

    def _load_model(self, model_name: str) -> WhisperModel:
        if self._model and self._model_name == model_name:
            return self._model
        log_event(
            self.logger,
            logging.INFO,
            "stt.model.load",
            "Loading faster-whisper model",
            model=model_name,
            compute_type=self._compute_type,
        )
        self._model = WhisperModel(model_name, compute_type=self._compute_type)
        self._model_name = model_name
        return self._model

    async def _transcribe_path(
        self, model: WhisperModel, file_path: Path, *, language: Optional[str], beam_size: int, vad_filter: bool
    ) -> tuple[list[Dict[str, Any]], Dict[str, Any]]:
        def _run():
            segments, info = model.transcribe(
                str(file_path),
                language=None if not language or language == "auto" else language,
                beam_size=beam_size,
                vad_filter=vad_filter,
            )
            output_segments = []
            for seg in segments:
                output_segments.append(
                    {
                        "text": seg.text.strip(),
                        "start": round(seg.start, 2),
                        "end": round(seg.end, 2),
                        "prob": seg.avg_logprob,
                    }
                )
            return output_segments, {"language": info.language, "duration": info.duration}

        return await asyncio.to_thread(_run)

    async def transcribe(self, audio_bytes: bytes, options: TranscriptionOptions) -> TranscriptionResult:
        model_name = options.model or self.settings.stt_default_model
        model = self._load_model(model_name)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp_file:
            tmp_path = Path(tmp_file.name)
            tmp_path.write_bytes(audio_bytes)

            stopwatch = Stopwatch()
            segments, _info = await self._transcribe_path(
                model,
                tmp_path,
                language=options.language,
                beam_size=options.beam_size,
                vad_filter=options.vad_filter,
            )
            timing_ms = {"transcribe": stopwatch.elapsed_ms(), "decode": stopwatch.elapsed_ms()}

        full_text = " ".join([seg.get("text", "") for seg in segments]).strip()
        return TranscriptionResult(
            text=full_text,
            segments=segments,
            provider=self.name,
            timing_ms=timing_ms,
        )

    def info(self) -> Dict[str, Any]:  # pragma: no cover - simple metadata
        return {
            "name": self.name,
            "model": self._model_name,
            "compute_type": self._compute_type,
        }
