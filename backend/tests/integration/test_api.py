import asyncio
import base64
import io
from uuid import UUID

import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.datastructures import UploadFile
from starlette.requests import Request
from starlette.testclient import TestClient

from app.api import routes_admin, routes_audio, routes_chat, routes_health
from app.common.errors import GatewayException
from app.models import ChatRequest, ProviderSelection


def _route_methods(app, path: str) -> set[str]:
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path == path:
            return set(route.methods or [])
    return set()


def _basic_request(app) -> Request:
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "path": "/",
        "raw_path": b"/",
        "headers": [],
        "query_string": b"",
        "server": ("testserver", 80),
        "client": ("testclient", 50000),
        "app": app,
    }
    return Request(scope)


def test_healthcheck(app_instance):
    client = TestClient(app_instance)
    response = client.get("/healthz")
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("status") == "ok"
    assert payload.get("app", {}).get("name") == "enterprise-ai-gateway"
    assert payload.get("app", {}).get("version")
    assert payload.get("runtime", {}).get("stt_provider")
    assert "uptime" in payload and payload["uptime"].get("seconds") is not None
    methods = _route_methods(app_instance, "/healthz")
    assert "POST" not in methods


def test_registry_returns_connectors(app_instance):
    request = _basic_request(app_instance)
    payload = asyncio.run(routes_admin.registry(request, app_instance.state.runtime))

    data = payload.model_dump()
    assert set(data.keys()) == {"llm", "rag", "stt", "tts", "servicedesk"}
    assert any(item["id"] == "mock-llm" for item in data["llm"])


def test_registry_invalid_method(app_instance):
    methods = _route_methods(app_instance, "/v1/registry")
    assert "POST" not in methods


def test_create_session_and_chat_flow(app_instance):
    runtime = app_instance.state.runtime
    session_response = asyncio.run(routes_chat.create_session(runtime))
    assert session_response.session_id
    UUID(session_response.session_id)

    chat_payload = ChatRequest(
        session_id=session_response.session_id,
        channel="web",
        message="hello gateway",
        provider_selection=ProviderSelection(
            llm_provider="mock-llm",
            llm_model="echo",
        ),
        use_rag=False,
        include_debug=True,
    )
    chat_response = asyncio.run(routes_chat.chat(chat_payload, _basic_request(app_instance), runtime))

    assert chat_response.session_id == session_response.session_id
    assert chat_response.reply
    assert chat_response.providers.llm_provider == "mock-llm"


def test_chat_rejects_unconfigured_provider(app_instance):
    runtime = app_instance.state.runtime
    chat_payload = ChatRequest(
        channel="web",
        message="try the wrong provider",
        provider_selection=ProviderSelection(
            llm_provider="azure-openai",
            llm_model="gpt-4o-mini",
        ),
        use_rag=False,
        include_debug=False,
    )

    with pytest.raises(GatewayException):
        asyncio.run(runtime.handle_chat(chat_payload, correlation_id=None))

    methods = _route_methods(app_instance, "/healthz")
    assert "POST" not in methods

def test_audio_transcribe_and_negative_provider(app_instance):
    runtime = app_instance.state.runtime
    audio_bytes = base64.b64decode(base64.b64encode(b"test audio"))

    transcript = asyncio.run(runtime.transcribe_audio("mock-stt", audio_bytes, locale="en-US", model="narrowband"))
    assert "text" in transcript

    with pytest.raises(GatewayException):
        asyncio.run(runtime.transcribe_audio("missing", audio_bytes, locale="en-US", model="narrowband"))


def test_transcribe_file_defaults(app_instance):
    runtime = app_instance.state.runtime
    upload = UploadFile(filename="test.wav", file=io.BytesIO(b"audio-bytes"))
    transcript = asyncio.run(
        routes_audio.transcribe_file(
            _basic_request(app_instance),
            file=upload,
            settings=None,
            runtime=runtime,
        )
    )

    assert transcript["settings_used"]["provider"] == "mock-stt"
    assert transcript["filename"] == "test.wav"
    assert "timing" in transcript and transcript["timing"]["received_bytes"] == len(b"audio-bytes")
    assert transcript["timing"].get("audio_seconds") is not None


def test_runtime_stats_endpoint(app_instance):
    client = TestClient(app_instance)
    response = client.get("/v1/runtime")
    assert response.status_code == 200
    data = response.json()
    assert data.get("backend_ready") is True
    assert data.get("runtime", {}).get("stt_provider")
    assert data.get("stats", {}).get("rolling_window_size") == 50


def test_transcribe_file_rejects_bad_settings(app_instance):
    runtime = app_instance.state.runtime
    upload = UploadFile(filename="test.wav", file=io.BytesIO(b"audio-bytes"))

    with pytest.raises(Exception):
        asyncio.run(
            routes_audio.transcribe_file(
                _basic_request(app_instance),
                file=upload,
                settings="not-json",
                runtime=runtime,
            )
        )


def test_transcribe_config_route():
    app = FastAPI()
    app.include_router(routes_audio.router)
    client = TestClient(app)
    response = client.get("/v1/audio/transcribe-config")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data and "languages" in data


def test_audio_synthesize_and_negative_provider(app_instance):
    runtime = app_instance.state.runtime
    response = asyncio.run(runtime.synthesize_audio("mock-tts", "hello", locale="en-US", voice="alloy"))

    assert response.get("audio") is not None

    with pytest.raises(GatewayException):
        asyncio.run(runtime.synthesize_audio("missing", "hello", locale="en-US", voice="alloy"))


def test_validate_connectors(app_instance):
    runtime = app_instance.state.runtime
    payload = asyncio.run(runtime.validate_connectors())
    assert payload.status in {"ok", "attention"}
    assert len(payload.results) > 0


def test_validate_connectors_invalid_method(app_instance):
    methods = _route_methods(app_instance, "/v1/admin/config/validate")
    assert "POST" not in methods


def test_create_session_invalid_method(app_instance):
    methods = _route_methods(app_instance, "/v1/sessions")
    assert "GET" not in methods
