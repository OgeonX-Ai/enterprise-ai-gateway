class _DummyMessage:
    def __init__(self, content: str = ""):  # noqa: D401
        self.content = content or ""


class _DummyChoice:
    def __init__(self, content: str = ""):
        self.message = _DummyMessage(content)


class _DummyUsage:
    def model_dump(self):
        return {}


class _DummyResponse:
    def __init__(self, content: str = ""):
        self.choices = [_DummyChoice(content or "stub response")]
        self.usage = _DummyUsage()


class _ChatCompletions:
    async def create(self, *args, **kwargs):
        return _DummyResponse()


class _Chat:
    def __init__(self):
        self.completions = _ChatCompletions()


class _Models:
    async def list(self):  # noqa: D401
        return {"data": []}


class AsyncAzureOpenAI:
    def __init__(self, *args, **kwargs):
        self.chat = _Chat()
        self.models = _Models()
