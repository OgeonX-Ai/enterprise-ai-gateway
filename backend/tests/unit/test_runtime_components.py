import pytest

from app.common.errors import PolicyViolation
from app.models import ChatMessage
from app.runtime.context_builder import ContextBuilder
from app.runtime.memory_store import MemoryStore
from app.runtime.policy import PolicyEngine
from app.runtime.router import RuntimeRouter


def test_memory_store_tracks_sessions():
    store = MemoryStore()
    store.create_session("session-1")
    store.append_turn("session-1", ChatMessage(role="user", content="hello"))

    assert len(store.history("session-1")) == 1
    assert store.history("session-1")[0].content == "hello"
    assert store.history("unknown") == []


def test_policy_engine_redacts_and_limits():
    engine = PolicyEngine()
    sanitized = engine.enforce("Customer SSN 123-45-6789 should be hidden")
    assert "[REDACTED]" in sanitized

    with pytest.raises(PolicyViolation):
        engine.enforce("x" * 4001)


def test_context_builder_appends_rag_snippets():
    builder = ContextBuilder()
    history = [ChatMessage(role="user", content="Hello")]
    rag_results = [
        {"snippet": "Important context A"},
        {"snippet": "Important context B"},
    ]

    conversation = builder.build(history, rag_results)

    assert conversation[0] == {"role": "user", "content": "Hello"}
    assert any(entry["role"] == "system" for entry in conversation)
    assert "Important context A" in conversation[-1]["content"]


def test_runtime_router_intents():
    router = RuntimeRouter()
    assert router.should_open_ticket("Please create an incident") == "create"
    assert router.should_open_ticket("status of existing request") == "status"
    assert router.should_open_ticket("no action needed") is None
