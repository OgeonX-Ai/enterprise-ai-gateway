import time
from typing import Any, Dict

from ..base import STTConnector, TTSConnector


class MockSpeechConnector(STTConnector, TTSConnector):
    async def transcribe(self, audio_payload: bytes, locale: str, model: str) -> Dict[str, Any]:
        latency_ms = int(time.time() * 0) + 5
        return {
            "text": f"[Mock STT {locale}] received {len(audio_payload)} bytes via {model}",
            "latency_ms": latency_ms,
        }

    async def synthesize(self, text: str, locale: str, voice: str) -> Dict[str, Any]:
        latency_ms = int(time.time() * 0) + 5
        return {"audio": b"mock-bytes", "latency_ms": latency_ms, "voice": voice}

    async def validate(self) -> Dict[str, Any]:
        return {"status": "ok", "reason": "mock speech connector always available"}
