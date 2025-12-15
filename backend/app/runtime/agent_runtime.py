import uuid
from typing import Any, Dict, Optional

from ..common.errors import GatewayException
from ..common.logging import bind_correlation_id, get_logger
from ..models import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    ProviderSelection,
    ValidationDetail,
    ValidationResponse,
)
from ..registry.service_registry import ServiceRegistry
from ..connectors.llm.mock_llm import MockLLMConnector
from ..connectors.llm.azure_openai import AzureOpenAIConnector
from ..connectors.rag.mock_search import MockSearchConnector
from ..connectors.rag.azure_ai_search import AzureAISearchConnector
from ..connectors.speech.mock_speech import MockSpeechConnector
from ..connectors.speech.azure_speech import AzureSpeechConnector
from ..connectors.servicedesk.mock_servicedesk import MockServiceDeskConnector
from ..connectors.servicedesk.servicenow import ServiceNowConnector
from ..connectors.servicedesk.jira_sm import JiraServiceManagementConnector
from ..connectors.servicedesk.remedy import RemedyConnector
from ..settings import Settings
from .context_builder import ContextBuilder
from .memory_store import MemoryStore
from .policy import PolicyEngine
from .router import RuntimeRouter


class AgentRuntime:
    def __init__(
        self,
        settings: Settings,
        registry: ServiceRegistry,
        memory: MemoryStore,
        context_builder: ContextBuilder,
        policy_engine: PolicyEngine,
        runtime_router: RuntimeRouter,
    ) -> None:
        self.settings = settings
        self.registry = registry
        self.memory = memory
        self.context_builder = context_builder
        self.policy_engine = policy_engine
        self.runtime_router = runtime_router
        self.logger = get_logger("agent_runtime")
        self.llm_connectors = self._build_llm_connectors()
        self.rag_connectors = self._build_rag_connectors()
        self.stt_connectors = self._build_stt_connectors()
        self.tts_connectors = self._build_tts_connectors()
        self.servicedesk_connectors = self._build_servicedesk_connectors()

    def _build_llm_connectors(self) -> Dict[str, Any]:
        connectors: Dict[str, Any] = {"mock-llm": MockLLMConnector()}
        if self.registry.is_configured("llm", "azure-openai"):
            connectors["azure-openai"] = AzureOpenAIConnector(
                endpoint=self.settings.azure_openai_endpoint or "",
                api_key=self.settings.azure_openai_api_key or "",
                api_version=self.settings.azure_openai_api_version or "",
                deployment_map={dep: dep for dep in self.registry.get_provider("llm", "azure-openai").supported},
            )
        return connectors

    def _build_rag_connectors(self) -> Dict[str, Any]:
        connectors: Dict[str, Any] = {"mock-search": MockSearchConnector()}
        if self.registry.is_configured("rag", "azure-ai-search"):
            connectors["azure-ai-search"] = AzureAISearchConnector(
                endpoint=self.settings.azure_search_endpoint or "",
                key=self.settings.azure_search_query_key or "",
            )
        return connectors

    def _build_stt_connectors(self) -> Dict[str, Any]:
        connectors: Dict[str, Any] = {"mock-stt": MockSpeechConnector()}
        if self.registry.is_configured("stt", "azure-speech"):
            connectors["azure-speech"] = AzureSpeechConnector(
                key=self.settings.azure_speech_key or "",
                region=self.settings.azure_speech_region or "",
            )
        return connectors

    def _build_tts_connectors(self) -> Dict[str, Any]:
        connectors: Dict[str, Any] = {"mock-tts": MockSpeechConnector()}
        if self.registry.is_configured("tts", "azure-speech"):
            connectors["azure-speech"] = AzureSpeechConnector(
                key=self.settings.azure_speech_key or "",
                region=self.settings.azure_speech_region or "",
            )
        return connectors

    def _build_servicedesk_connectors(self) -> Dict[str, Any]:
        connectors: Dict[str, Any] = {"mock-servicedesk": MockServiceDeskConnector()}
        if self.registry.is_configured("servicedesk", "servicenow"):
            connectors["servicenow"] = ServiceNowConnector(
                instance_url=self.settings.servicenow_instance_url or "",
                client_id=self.settings.servicenow_client_id or "",
                client_secret=self.settings.servicenow_client_secret or "",
            )
        if self.registry.is_configured("servicedesk", "jira-sm"):
            connectors["jira-sm"] = JiraServiceManagementConnector(
                base_url=self.settings.jira_base_url or "",
                email=self.settings.jira_email or "",
                api_token=self.settings.jira_api_token or "",
            )
        if self.registry.is_configured("servicedesk", "remedy"):
            connectors["remedy"] = RemedyConnector(
                base_url=self.settings.remedy_base_url or "",
                username=self.settings.remedy_username or "",
                password=self.settings.remedy_password or "",
            )
        return connectors

    def _get_session_id(self, provided: Optional[str]) -> str:
        return provided or str(uuid.uuid4())

    async def handle_chat(self, request: ChatRequest, correlation_id: Optional[str]) -> ChatResponse:
        logger = bind_correlation_id(self.logger, correlation_id)
        session_id = self._get_session_id(request.session_id)
        self.memory.create_session(session_id)

        if not self.registry.is_configured("llm", request.provider_selection.llm_provider):
            missing = self.registry.missing_env("llm", request.provider_selection.llm_provider)
            raise GatewayException(f"LLM provider not configured; missing env: {', '.join(missing)}")

        sanitized_message = self.policy_engine.enforce(request.message)
        user_message = ChatMessage(role="user", content=sanitized_message)
        self.memory.append_turn(session_id, user_message)

        rag_results = []
        if request.use_rag and request.provider_selection.rag_provider:
            if not self.registry.is_configured("rag", request.provider_selection.rag_provider):
                missing = self.registry.missing_env("rag", request.provider_selection.rag_provider)
                raise GatewayException(f"RAG provider not configured; missing env: {', '.join(missing)}")
            rag_connector = self.rag_connectors.get(request.provider_selection.rag_provider)
            if not rag_connector:
                raise GatewayException("RAG provider not found")
            rag_results = await rag_connector.search(
                request.message, top_k=3, index_name=request.provider_selection.rag_index or "default"
            )

        history = self.memory.history(session_id)
        llm_messages = self.context_builder.build(history, rag_results)
        llm_connector = self.llm_connectors.get(request.provider_selection.llm_provider)
        if not llm_connector:
            raise GatewayException("LLM provider not found")
        llm_result = await llm_connector.generate(
            llm_messages,
            model=request.provider_selection.llm_model,
            temperature=0.2,
            max_tokens=256,
        )
        llm_reply = llm_result.get("text", "")

        servicedesk_action = None
        servicedesk_payload: Dict[str, Any] = {}
        if request.provider_selection.servicedesk_provider:
            if not self.registry.is_configured("servicedesk", request.provider_selection.servicedesk_provider):
                missing = self.registry.missing_env("servicedesk", request.provider_selection.servicedesk_provider)
                raise GatewayException(f"Service desk provider not configured; missing env: {', '.join(missing)}")
            intent = self.runtime_router.should_open_ticket(request.message)
            if intent and request.provider_selection.servicedesk_provider in self.servicedesk_connectors:
                connector = self.servicedesk_connectors[request.provider_selection.servicedesk_provider]
                if intent == "create":
                    servicedesk_payload = await connector.create_ticket(
                        "AI Gateway Ticket", request.message, severity="3", requester=None
                    )
                elif intent == "status":
                    servicedesk_payload = await connector.get_ticket("SNOW-1001")
                servicedesk_action = intent

        assistant_message = ChatMessage(role="assistant", content=llm_reply)
        self.memory.append_turn(session_id, assistant_message)

        debug: Optional[Dict[str, Any]] = None
        if request.include_debug or self.settings.dev_mode:
            debug = {
                "correlation_id": correlation_id,
                "rag_results": rag_results,
                "servicedesk": servicedesk_payload,
                "history_length": len(history) + 1,
                "llm_usage": llm_result.get("usage", {}),
                "latency_ms": llm_result.get("latency_ms"),
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

    async def transcribe_audio(self, provider_id: str, payload: bytes, locale: str, model: str) -> Dict[str, Any]:
        connector = self.stt_connectors.get(provider_id)
        if not connector:
            raise GatewayException("STT provider not found")
        return await connector.transcribe(payload, locale=locale, model=model)

    async def synthesize_audio(self, provider_id: str, text: str, locale: str, voice: Optional[str] = None) -> Dict[str, Any]:
        connector = self.tts_connectors.get(provider_id)
        if not connector:
            raise GatewayException("TTS provider not found")
        return await connector.synthesize(text, locale=locale, voice=voice or "")

    def registry_snapshot(self) -> Dict[str, Any]:
        providers = self.registry.list_providers(include_unconfigured=self.settings.dev_mode)
        return {key: [item.model_dump() for item in value] for key, value in providers.items()}

    async def validate_connectors(self) -> ValidationResponse:
        details: list[ValidationDetail] = []
        for service_type, connectors in [
            ("llm", self.llm_connectors),
            ("rag", self.rag_connectors),
            ("stt", self.stt_connectors),
            ("tts", self.tts_connectors),
            ("servicedesk", self.servicedesk_connectors),
        ]:
            for provider_id, connector in connectors.items():
                provider = self.registry.get_provider(service_type, provider_id)
                if not provider.configured:
                    details.append(
                        ValidationDetail(
                            service_type=service_type,
                            provider=provider_id,
                            status="not_configured",
                            reason=f"Missing env: {', '.join(provider.missing_env)}" if provider.missing_env else "Disabled",
                        )
                    )
                    continue
                try:
                    result = await connector.validate()
                    details.append(
                        ValidationDetail(
                            service_type=service_type,
                            provider=provider_id,
                            status=result.get("status", "unknown"),
                            reason=result.get("reason", ""),
                        )
                    )
                except Exception as exc:  # noqa: BLE001
                    details.append(
                        ValidationDetail(
                            service_type=service_type,
                            provider=provider_id,
                            status="error",
                            reason=str(exc),
                        )
                    )
        overall_status = "ok" if all(item.status == "ok" for item in details if self.registry.is_configured(item.service_type, item.provider)) else "attention"
        return ValidationResponse(status=overall_status, results=details)
