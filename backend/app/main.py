from fastapi import FastAPI

from .connectors import MockLLMConnector, MockServiceDeskConnector, MockSpeechConnector
from .memory import MemoryStore
from .registry import ConnectorRegistry
from .router import create_router


def build_app() -> FastAPI:
    app = FastAPI(title="Enterprise AI Gateway", version="0.1.0")

    memory = MemoryStore()
    registry = ConnectorRegistry()
    registry.register(MockLLMConnector())
    registry.register(MockSpeechConnector())
    registry.register(MockServiceDeskConnector())

    app.include_router(create_router(memory=memory, registry=registry))
    return app


app = build_app()
