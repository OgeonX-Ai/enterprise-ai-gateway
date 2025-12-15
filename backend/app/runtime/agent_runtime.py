import uuid
from typing import Any, Dict, Optional

from ..common.errors import GatewayException
from ..common.logging import bind_correlation_id, get_logger
from ..models import ChatMessage, ChatRequest, ChatResponse, ProviderSelection
from ..registry.service_registry import ServiceRegistry
from ..connectors.llm.mock_llm import MockLLMConnector
from ..connectors.llm.azure_openai_stub import AzureOpenAIStub
from ..connectors.rag.mock_search import MockSearchConnector
from ..connectors.rag.azure_ai_search_stub import AzureAISearchStub
from ..connectors.speech.mock_speech import MockSpeechConnector
from ..connectors.speech.azure_speech_stub import AzureSpeechStub
from ..connectors.servicedesk.servicenow_stub import ServiceNowStub
from ..connectors.servicedesk.remedy_stub import RemedyStub
from ..connectors.servicedesk.jira_sm_stub import JiraServiceManagementStub
from .context_builder import ContextBuilder
from .memory_store import MemoryStore
from .policy import PolicyEngine
from .router import RuntimeRouter


class AgentRuntime:
    def __init__(
        self,
        registry: ServiceRegistry,
        memory: MemoryStore,
        context_builder: ContextBuilder,
        policy_engine: PolicyEngine,
        runtime_router: RuntimeRouter,
    ) -> None:
        self.registry = registry
        self.memory = memory
        self.context_builder = context_builder
        self.policy_engine = policy_engine
        self.runtime_router = runtime_router
        self.logger = get_logger("agent_runtime")
        self.llm_connectors = {
            "mock-llm": MockLLMConnector(),
            "azure-openai": AzureOpenAIStub(),
        }
        self.rag_connectors = {
            "mock-search": MockSearchConnector(),
            "azure-ai-search": AzureAISearchStub(),
        }
        self.speech_connectors = {
            "mock-stt": MockSpeechConnector(),
            "mock-tts": MockSpeechConnector(),
            "azure-speech-stt": AzureSpeechStub(),
            "azure-speech-tts": AzureSpeechStub(),
        }
        self.servicedesk_connectors = {
            "servicenow": ServiceNowStub(),
            "remedy": RemedyStub(),
            "jira-sm": JiraServiceManagementStub(),
        }

    def _get_session_id(self, provided: Optional[str]) -> str:
        return provided or str(uuid.uuid4())

    async def handle_chat(self, request: ChatRequest, correlation_id: Optional[str]) -> ChatResponse:
        logger = bind_correlation_id(self.logger, correlation_id)
        session_id = self._get_session_id(request.session_id)
        self.memory.create_session(session_id)

        sanitized_message = self.policy_engine.enforce(request.message)
        user_message = ChatMessage(role="user", content=sanitized_message)
        self.memory.append_turn(session_id, user_message)

        rag_results = []
        if request.use_rag and request.provider_selection.rag_provider:
            rag_connector = self.rag_connectors.get(request.provider_selection.rag_provider)
            if not rag_connector:
                raise GatewayException("RAG provider not found")
            rag_results = await rag_connector.search(request.message)

        history = self.memory.history(session_id)
        llm_messages = self.context_builder.build(history, rag_results)
        llm_connector = self.llm_connectors.get(request.provider_selection.llm_provider)
        if not llm_connector:
            raise GatewayException("LLM provider not found")
        llm_reply = await llm_connector.generate(
            llm_messages,
            {"model": request.provider_selection.llm_model, "channel": request.channel},
        )

        servicedesk_action = None
        servicedesk_payload: Dict[str, Any] = {}
        if request.provider_selection.servicedesk_provider:
            intent = self.runtime_router.should_open_ticket(request.message)
            if intent and request.provider_selection.servicedesk_provider in self.servicedesk_connectors:
                connector = self.servicedesk_connectors[request.provider_selection.servicedesk_provider]
                if intent == "create":
                    servicedesk_payload = await connector.create_ticket("AI Gateway Ticket", request.message)
                elif intent == "status":
                    servicedesk_payload = await connector.get_ticket("SNOW-1001")
                servicedesk_action = intent

        assistant_message = ChatMessage(role="assistant", content=llm_reply)
        self.memory.append_turn(session_id, assistant_message)

        debug: Optional[Dict[str, Any]] = None
        if request.include_debug:
            debug = {
                "correlation_id": correlation_id,
                "rag_results": rag_results,
                "servicedesk": servicedesk_payload,
                "history_length": len(history) + 1,
            }
            logger.info(
                "Runtime executed",
                extra={
                    "providers": request.provider_selection.model_dump(),
                    "used_rag": bool(rag_results),
                    "servicedesk_action": servicedesk_action,
                },
            )

        return ChatResponse(
            session_id=session_id,
            reply=llm_reply,
            providers=request.provider_selection,
            used_rag=bool(rag_results),
            servicedesk_action=servicedesk_action,
            debug=debug,
        )

    async def transcribe_audio(self, provider_id: str, payload: bytes) -> str:
        connector = self.speech_connectors.get(provider_id)
        if not connector:
            raise GatewayException("STT provider not found")
        return await connector.transcribe(payload, {})

    async def synthesize_audio(self, provider_id: str, text: str, voice: Optional[str] = None) -> str:
        connector = self.speech_connectors.get(provider_id)
        if not connector:
            raise GatewayException("TTS provider not found")
        return await connector.synthesize(text, {"voice": voice})

    def registry_snapshot(self) -> Dict[str, Any]:
        return {
            key: [item.model_dump() for item in value]
            for key, value in self.registry.list_providers().items()
        }
