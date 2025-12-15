import io
import time
from typing import Any, Dict

import azure.cognitiveservices.speech as speechsdk

from ..base import STTConnector, TTSConnector


class AzureSpeechConnector(STTConnector, TTSConnector):
    def __init__(self, key: str, region: str) -> None:
        self.key = key
        self.region = region

    def _speech_config(self, locale: str | None = None) -> speechsdk.SpeechConfig:
        config = speechsdk.SpeechConfig(subscription=self.key, region=self.region)
        if locale:
            config.speech_recognition_language = locale
            config.speech_synthesis_language = locale
        return config

    async def transcribe(self, audio_payload: bytes, locale: str, model: str) -> Dict[str, Any]:
        start = time.time()
        config = self._speech_config(locale)
        stream = speechsdk.audio.PushAudioInputStream()
        stream.write(audio_payload)
        stream.close()
        audio_config = speechsdk.audio.AudioConfig(stream=stream)
        recognizer = speechsdk.SpeechRecognizer(speech_config=config, audio_config=audio_config)
        result = recognizer.recognize_once_async().get()
        latency_ms = int((time.time() - start) * 1000)
        return {"text": result.text or "", "latency_ms": latency_ms, "model": model}

    async def synthesize(self, text: str, locale: str, voice: str) -> Dict[str, Any]:
        start = time.time()
        config = self._speech_config(locale)
        if voice:
            config.speech_synthesis_voice_name = voice
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=config, audio_config=None)
        result = synthesizer.speak_text_async(text).get()
        latency_ms = int((time.time() - start) * 1000)
        audio_data = io.BytesIO(result.audio_data).getvalue() if result and result.audio_data else b""
        return {"audio": audio_data, "latency_ms": latency_ms, "voice": voice}

    async def validate(self) -> Dict[str, Any]:
        try:
            config = self._speech_config()
            _ = config.subscription
            return {"status": "ok", "reason": "Azure Speech credentials loaded"}
        except Exception as exc:  # noqa: BLE001
            return {"status": "error", "reason": str(exc)}
