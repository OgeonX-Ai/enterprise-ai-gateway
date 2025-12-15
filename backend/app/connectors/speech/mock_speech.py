from typing import Any, Dict

from ..base import SpeechConnector


class MockSpeechConnector(SpeechConnector):
    async def transcribe(self, audio_payload: bytes, settings: Dict[str, Any]) -> str:
        return "[MockSTT] Transcription placeholder for provided audio payload"

    async def synthesize(self, text: str, settings: Dict[str, Any]) -> str:
        voice = settings.get("voice", "alloy")
        return f"[MockTTS:{voice}] Audio bytes for text: {text[:60]}..."
