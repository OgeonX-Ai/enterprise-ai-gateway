from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from ...common.logging import bind_correlation_id, get_logger, log_event
from ...settings import Settings
from .base import SpeechProviderError, TranscriptionOptions, TranscriptionResult
from .elevenlabs_stt import ElevenLabsProvider
from .local_whisper_stt import LocalWhisperProvider


@dataclass
class SpeechRouterStatus:
    stt_provider_active: str
    elevenlabs_ok: bool
    last_error: Optional[str]
    last_error_at: Optional[datetime]
    mode: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, object]:  # pragma: no cover - serialization helper
        return {
            "stt_provider_active": self.stt_provider_active,
            "elevenlabs_ok": self.elevenlabs_ok,
            "last_error": self.last_error,
            "last_error_at": self.last_error_at.isoformat() if self.last_error_at else None,
            "mode": self.mode,
            "timestamp": self.timestamp.isoformat(),
        }


class SpeechRouter:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = bind_correlation_id(get_logger(__name__), None)
        self.providers: Dict[str, object] = {
            "local_whisper": LocalWhisperProvider(settings),
        }
        if settings.elevenlabs_api_key:
            self.providers["elevenlabs"] = ElevenLabsProvider(settings)
        self.last_elevenlabs_failure: Optional[datetime] = None
        self.last_error: Optional[str] = None
        self.last_provider_used: str = settings.stt_provider

    def _elevenlabs_in_cooldown(self) -> bool:
        if not self.last_elevenlabs_failure:
            return False
        return datetime.now(timezone.utc) - self.last_elevenlabs_failure < timedelta(minutes=10)

    def _mark_elevenlabs_failure(self, message: str) -> None:
        self.last_elevenlabs_failure = datetime.now(timezone.utc)
        self.last_error = message
        log_event(
            self.logger,
            logging.WARN,
            "stt.provider.unavailable",
            "ElevenLabs marked unavailable",
            reason=message,
        )

    def _select_primary(self, requested: str) -> str:
        if requested == "auto":
            if "elevenlabs" in self.providers and not self._elevenlabs_in_cooldown():
                return "elevenlabs"
            return "local_whisper"
        return requested

    def _build_options(
        self, *, language: Optional[str], beam_size: int, vad: bool, model: Optional[str]
    ) -> TranscriptionOptions:
        language_opt = language if language and language != "auto" else None
        return TranscriptionOptions(language=language_opt, beam_size=beam_size, vad_filter=vad, model=model)

    def status(self) -> SpeechRouterStatus:
        return SpeechRouterStatus(
            stt_provider_active=self.last_provider_used,
            elevenlabs_ok="elevenlabs" in self.providers and not self._elevenlabs_in_cooldown(),
            last_error=self.last_error,
            last_error_at=self.last_elevenlabs_failure,
            mode="fallback" if self._elevenlabs_in_cooldown() else "primary",
        )

    async def transcribe(
        self,
        audio_bytes: bytes,
        *,
        provider: str,
        language: Optional[str],
        beam_size: int,
        vad: bool,
        model: Optional[str],
        correlation_id: Optional[str],
    ) -> TranscriptionResult:
        provider = provider or "auto"
        options = self._build_options(language=language, beam_size=beam_size, vad=vad, model=model)
        primary = self._select_primary(provider)
        mode = "primary"
        logger = bind_correlation_id(self.logger, correlation_id)
        provider_instance = self.providers.get(primary)

        if not provider_instance:
            raise SpeechProviderError("provider_unavailable", f"Provider {primary} is not available")

        try:
            log_event(
                logger,
                logging.INFO,
                "stt.transcribe.start",
                "Transcription starting",
                provider=primary,
                language=options.language or "auto",
                model=options.model,
            )
            result: TranscriptionResult = await provider_instance.transcribe(audio_bytes, options)
            result.mode = mode
            self.last_provider_used = result.provider
            return result
        except SpeechProviderError as exc:
            log_event(
                logger,
                logging.WARN,
                "stt.provider.error",
                "Transcription provider error",
                provider=primary,
                code=exc.code,
            )
            if primary == "elevenlabs" and exc.credit_issue:
                self._mark_elevenlabs_failure(str(exc))
                fallback = self.providers.get("local_whisper")
                if provider == "elevenlabs" and not fallback:
                    raise
                if fallback:
                    mode = "fallback"
                    log_event(
                        logger,
                        logging.INFO,
                        "stt.fallback",
                        "Falling back to local whisper",
                        reason=exc.code,
                    )
                    result = await fallback.transcribe(audio_bytes, options)
                    result.mode = mode
                    self.last_provider_used = result.provider
                    return result
            raise
        except Exception as exc:  # noqa: BLE001
            log_event(
                logger,
                logging.ERROR,
                "stt.transcribe.unexpected",
                "Unexpected transcription error",
                provider=primary,
                exc_info=exc,
            )
            raise
