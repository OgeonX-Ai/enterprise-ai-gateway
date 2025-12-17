from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Optional


class SpeechProviderError(Exception):
    """Error raised by speech providers to convey actionable hints."""

    def __init__(self, code: str, message: str, *, hint: Optional[str] = None, credit_issue: bool = False):
        super().__init__(message)
        self.code = code
        self.hint = hint
        self.credit_issue = credit_issue

    def to_dict(self) -> Dict[str, Any]:  # pragma: no cover - simple mapper
        payload = {"code": self.code, "message": str(self)}
        if self.hint:
            payload["hint"] = self.hint
        return payload


@dataclass
class TranscriptionOptions:
    language: Optional[str] = None
    model: Optional[str] = None
    beam_size: int = 1
    vad_filter: bool = False


@dataclass
class TranscriptionResult:
    text: str
    segments: list[Dict[str, Any]]
    provider: str
    timing_ms: Dict[str, float]
    mode: str = "primary"


class SpeechProvider:
    name: str = "base"

    async def transcribe(self, audio_bytes: bytes, options: TranscriptionOptions) -> TranscriptionResult:
        raise NotImplementedError

    def info(self) -> Dict[str, Any]:  # pragma: no cover - trivial metadata
        return {"name": self.name}


class Stopwatch:
    def __init__(self) -> None:
        self._start = time.perf_counter()

    def elapsed_ms(self) -> float:
        return round((time.perf_counter() - self._start) * 1000, 2)
