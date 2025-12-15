from typing import Any, Dict

from ..base import SpeechConnector


class AzureSpeechStub(SpeechConnector):
    async def transcribe(self, audio_payload: bytes, settings: Dict[str, Any]) -> str:
        locale = settings.get("locale", "en-US")
        return f"[Azure Speech STT stub] Locale {locale}; would call Azure Cognitive Services."

    async def synthesize(self, text: str, settings: Dict[str, Any]) -> str:
        voice = settings.get("voice", "en-US-JennyNeural")
        return f"[Azure Speech TTS stub] Voice {voice}; synthesized audio for: {text[:60]}..."
