class SpeechConfig:
    def __init__(self, subscription: str | None = None, region: str | None = None):
        self.subscription = subscription
        self.region = region
        self.speech_recognition_language = None
        self.speech_synthesis_language = None


class _AudioModule:
    class PushAudioInputStream:
        def __init__(self):
            self._buffer = bytearray()

        def write(self, data: bytes):
            self._buffer.extend(data)

        def close(self):
            return None

    class AudioConfig:
        def __init__(self, stream=None):
            self.stream = stream


audio = _AudioModule()


class _Result:
    def __init__(self, text: str = "", audio_data: bytes | None = None):
        self.text = text
        self.audio_data = audio_data or b""


class SpeechRecognizer:
    def __init__(self, speech_config=None, audio_config=None):
        self.speech_config = speech_config
        self.audio_config = audio_config

    class _AsyncResult:
        def __init__(self, result):
            self._result = result

        def get(self):
            return self._result

    def recognize_once_async(self):
        return self._AsyncResult(_Result(""))


class SpeechSynthesizer:
    def __init__(self, speech_config=None, audio_config=None):
        self.speech_config = speech_config
        self.audio_config = audio_config

    class _AsyncResult:
        def __init__(self, result):
            self._result = result

        def get(self):
            return self._result

    def speak_text_async(self, text: str):
        return self._AsyncResult(_Result("", audio_data=b""))
