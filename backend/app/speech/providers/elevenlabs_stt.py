from __future__ import annotations

import json
from typing import Any, Dict, Optional

import httpx

from ...common.logging import get_logger
from ...settings import Settings
from .base import SpeechProvider, SpeechProviderError, Stopwatch, TranscriptionOptions, TranscriptionResult


class ElevenLabsProvider(SpeechProvider):
    name = "elevenlabs"

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        self._api_key = settings.elevenlabs_api_key
        self._model_id = settings.elevenlabs_model_id

    def _client(self) -> httpx.AsyncClient:
        headers = {"xi-api-key": self._api_key or ""}
        return httpx.AsyncClient(timeout=30.0, headers=headers)

    async def transcribe(self, audio_bytes: bytes, options: TranscriptionOptions) -> TranscriptionResult:
        if not self._api_key:
            raise SpeechProviderError(
                "not_configured", "ElevenLabs API key missing", hint="Set ELEVENLABS_API_KEY to enable ElevenLabs"
            )

        stopwatch = Stopwatch()
        async with self._client() as client:
            files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
            data = {
                "model_id": options.model or self._model_id,
            }
            if options.language and options.language != "auto":
                data["language_code"] = options.language
            response = await client.post("https://api.elevenlabs.io/v1/audio/transcriptions", files=files, data=data)

        elapsed = stopwatch.elapsed_ms()
        if response.status_code >= 400:
            message = self._extract_error(response)
            credit_issue = response.status_code in {401, 402, 403, 429}
            raise SpeechProviderError(
                f"http_{response.status_code}",
                message,
                hint="Check ElevenLabs credits or API key",
                credit_issue=credit_issue,
            )

        payload = response.json()
        text = payload.get("text") or payload.get("transcription") or ""
        segments = payload.get("segments") or []
        return TranscriptionResult(
            text=text,
            segments=segments if isinstance(segments, list) else [],
            provider=self.name,
            timing_ms={"transcribe": elapsed},
        )

    def _extract_error(self, response: httpx.Response) -> str:
        try:
            data = response.json()
            if isinstance(data, dict):
                return data.get("detail") or data.get("error") or json.dumps(data)
        except Exception:  # noqa: BLE001 pragma: no cover - fallback only
            return response.text[:500]
        return response.text[:500]
