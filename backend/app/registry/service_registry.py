from typing import Dict, List

from .models import ServiceProvider


class ServiceRegistry:
    def __init__(self) -> None:
        self.providers: Dict[str, List[ServiceProvider]] = {
            "llm": [
                ServiceProvider(
                    id="mock-llm",
                    display_name="Mock LLM",
                    capabilities=["chat"],
                    supported=["echo", "assistant-lite"],
                    requires_auth=False,
                ),
                ServiceProvider(
                    id="azure-openai",
                    display_name="Azure OpenAI (stub)",
                    capabilities=["chat", "completion"],
                    supported=["gpt-4o-mini"],
                    requires_auth=True,
                ),
            ],
            "rag": [
                ServiceProvider(
                    id="mock-search",
                    display_name="Mock Search",
                    capabilities=["keyword", "hybrid"],
                    supported=["default"],
                    requires_auth=False,
                ),
                ServiceProvider(
                    id="azure-ai-search",
                    display_name="Azure AI Search (stub)",
                    capabilities=["semantic", "vector"],
                    supported=["contoso-knowledge"],
                    requires_auth=True,
                ),
            ],
            "stt": [
                ServiceProvider(
                    id="mock-stt",
                    display_name="Mock Speech-to-Text",
                    capabilities=["en-US"],
                    supported=["narrowband"],
                    requires_auth=False,
                ),
                ServiceProvider(
                    id="azure-speech-stt",
                    display_name="Azure Speech STT (stub)",
                    capabilities=["en-US", "es-ES"],
                    supported=["conversational"],
                    requires_auth=True,
                ),
            ],
            "tts": [
                ServiceProvider(
                    id="mock-tts",
                    display_name="Mock Text-to-Speech",
                    capabilities=["en-US"],
                    supported=["alloy"],
                    requires_auth=False,
                ),
                ServiceProvider(
                    id="azure-speech-tts",
                    display_name="Azure Speech TTS (stub)",
                    capabilities=["en-US", "en-GB"],
                    supported=["neural"],
                    requires_auth=True,
                ),
            ],
            "servicedesk": [
                ServiceProvider(
                    id="servicenow",
                    display_name="ServiceNow (stub)",
                    capabilities=["create", "update", "status"],
                    supported=["incident"],
                    requires_auth=True,
                ),
                ServiceProvider(
                    id="remedy",
                    display_name="BMC Remedy (stub)",
                    capabilities=["create", "status"],
                    supported=["incident"],
                    requires_auth=True,
                ),
                ServiceProvider(
                    id="jira-sm",
                    display_name="Jira Service Management (stub)",
                    capabilities=["create", "comment", "status"],
                    supported=["service-request"],
                    requires_auth=True,
                ),
            ],
        }

    def list_providers(self) -> Dict[str, List[ServiceProvider]]:
        return self.providers

    def get_provider(self, service_type: str, provider_id: str) -> ServiceProvider:
        for provider in self.providers.get(service_type, []):
            if provider.id == provider_id:
                return provider
        raise ValueError(f"Provider {provider_id} not found for {service_type}")
