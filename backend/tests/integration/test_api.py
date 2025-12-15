import base64
from uuid import UUID

from fastapi.testclient import TestClient


def test_healthcheck(client: TestClient):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_healthcheck_rejects_invalid_method(client: TestClient):
    response = client.post("/healthz")
    assert response.status_code == 405


def test_registry_returns_connectors(client: TestClient):
    response = client.get("/v1/registry")
    payload = response.json()

    assert response.status_code == 200
    assert set(payload.keys()) == {"llm", "rag", "stt", "tts", "servicedesk"}
    assert any(item["id"] == "mock-llm" for item in payload["llm"])


def test_registry_invalid_method(client: TestClient):
    response = client.post("/v1/registry")
    assert response.status_code == 405


def test_create_session_and_chat_flow(client: TestClient):
    session_response = client.post("/v1/sessions")
    assert session_response.status_code == 200

    session_id = session_response.json()["session_id"]
    UUID(session_id)

    chat_payload = {
        "session_id": session_id,
        "channel": "web",
        "message": "hello gateway",
        "provider_selection": {
            "llm_provider": "mock-llm",
            "llm_model": "echo",
            "rag_provider": None,
            "rag_index": None,
            "stt_provider": None,
            "stt_model": None,
            "tts_provider": None,
            "tts_voice": None,
            "servicedesk_provider": None,
        },
        "use_rag": False,
        "include_debug": True,
    }
    chat_response = client.post("/v1/chat", json=chat_payload)

    assert chat_response.status_code == 200
    body = chat_response.json()
    assert body["session_id"] == session_id
    assert "reply" in body and body["reply"]
    assert body["providers"]["llm_provider"] == "mock-llm"


def test_chat_rejects_unconfigured_provider(client: TestClient):
    chat_payload = {
        "channel": "web",
        "message": "try the wrong provider",
        "provider_selection": {
            "llm_provider": "azure-openai",
            "llm_model": "gpt-4o-mini",
            "rag_provider": None,
            "rag_index": None,
            "stt_provider": None,
            "stt_model": None,
            "tts_provider": None,
            "tts_voice": None,
            "servicedesk_provider": None,
        },
        "use_rag": False,
        "include_debug": False,
    }
    response = client.post("/v1/chat", json=chat_payload)

    assert response.status_code == 400
    assert "LLM provider not configured" in response.json().get("detail", "")


def test_audio_transcribe_and_negative_provider(client: TestClient):
    audio_base64 = base64.b64encode(b"test audio").decode()
    response = client.post(
        "/v1/audio/transcribe",
        json={"audio_base64": audio_base64, "locale": "en-US", "model": "narrowband"},
    )

    assert response.status_code == 200
    assert "text" in response.json()

    missing = client.post(
        "/v1/audio/transcribe",
        json={"stt_provider": "missing", "audio_base64": audio_base64},
    )
    assert missing.status_code == 400


def test_audio_synthesize_and_negative_provider(client: TestClient):
    response = client.post(
        "/v1/audio/synthesize",
        json={"text": "hello", "locale": "en-US", "voice": "alloy"},
    )

    assert response.status_code == 200
    assert response.json()["audio_base64"]

    missing = client.post(
        "/v1/audio/synthesize",
        json={"text": "hello", "tts_provider": "missing"},
    )
    assert missing.status_code == 400


def test_validate_connectors(client: TestClient):
    response = client.get("/v1/admin/config/validate")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"ok", "attention"}
    assert len(payload["results"]) > 0


def test_validate_connectors_invalid_method(client: TestClient):
    response = client.post("/v1/admin/config/validate")
    assert response.status_code == 405


def test_create_session_invalid_method(client: TestClient):
    response = client.get("/v1/sessions")
    assert response.status_code == 405
