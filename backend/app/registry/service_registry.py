from typing import Dict, List

from ..settings import Settings
from .models import ServiceProvider


class ServiceRegistry:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.providers: Dict[str, List[ServiceProvider]] = {
            "llm": [
                ServiceProvider(
                    id="mock-llm",
                    display_name="Mock LLM",
                    capabilities=["chat"],
                    supported=["echo", "assistant-lite"],
                    requires_auth=False,
                    configured=True,
                )
            ],
            "rag": [
                ServiceProvider(
                    id="mock-search",
                    display_name="Mock Search",
                    capabilities=["keyword", "hybrid"],
                    supported=["default"],
                    requires_auth=False,
                    configured=True,
                )
            ],
            "stt": [
                ServiceProvider(
                    id="mock-stt",
                    display_name="Mock Speech-to-Text",
                    capabilities=["en-US"],
                    supported=["narrowband"],
                    requires_auth=False,
                    configured=True,
                )
            ],
            "tts": [
                ServiceProvider(
                    id="mock-tts",
                    display_name="Mock Text-to-Speech",
                    capabilities=["en-US"],
                    supported=["alloy"],
                    requires_auth=False,
                    configured=True,
                )
            ],
            "servicedesk": [
                ServiceProvider(
                    id="mock-servicedesk",
                    display_name="Mock Service Desk",
                    capabilities=["create", "status"],
                    supported=["incident"],
                    requires_auth=False,
                    configured=True,
                )
            ],
        }
        self._attach_real_providers()

    def _attach_real_providers(self) -> None:
        aoai_missing = [env for env, val in {
            "AZURE_OPENAI_ENDPOINT": self.settings.azure_openai_endpoint,
            "AZURE_OPENAI_API_KEY": self.settings.azure_openai_api_key,
        }.items() if not val]
        aoai_configured = self.settings.use_azure_openai and not aoai_missing
        self._maybe_add(
            "llm",
            ServiceProvider(
                id="azure-openai",
                display_name="Azure OpenAI",
                capabilities=["chat", "completion"],
                supported=self.settings.azure_openai_deployments or ["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1"],
                requires_auth=True,
                configured=aoai_configured,
                status="configured" if aoai_configured else "missing_env",
                missing_env=aoai_missing,
            ),
        )

        search_missing = [env for env, val in {
            "AZURE_SEARCH_ENDPOINT": self.settings.azure_search_endpoint,
            "AZURE_SEARCH_QUERY_KEY": self.settings.azure_search_query_key,
        }.items() if not val]
        search_configured = self.settings.use_azure_search and not search_missing
        self._maybe_add(
            "rag",
            ServiceProvider(
                id="azure-ai-search",
                display_name="Azure AI Search",
                capabilities=["keyword", "vector"],
                supported=[self.settings.azure_search_index_default or "default"],
                requires_auth=True,
                configured=search_configured,
                status="configured" if search_configured else "missing_env",
                missing_env=search_missing,
            ),
        )

        speech_missing = [env for env, val in {
            "AZURE_SPEECH_KEY": self.settings.azure_speech_key,
            "AZURE_SPEECH_REGION": self.settings.azure_speech_region,
        }.items() if not val]
        speech_configured = self.settings.use_azure_speech and not speech_missing
        speech_provider = ServiceProvider(
            id="azure-speech",
            display_name="Azure Speech",
            capabilities=["stt", "tts"],
            supported=["conversational"],
            requires_auth=True,
            configured=speech_configured,
            status="configured" if speech_configured else "missing_env",
            missing_env=speech_missing,
        )
        self._maybe_add("stt", speech_provider)
        self._maybe_add(
            "tts",
            ServiceProvider(**speech_provider.model_dump()),
        )

        sn_missing = [env for env, val in {
            "SERVICENOW_INSTANCE_URL": self.settings.servicenow_instance_url,
            "SERVICENOW_CLIENT_ID": self.settings.servicenow_client_id,
            "SERVICENOW_CLIENT_SECRET": self.settings.servicenow_client_secret,
        }.items() if not val]
        sn_configured = self.settings.use_servicenow and not sn_missing
        self._maybe_add(
            "servicedesk",
            ServiceProvider(
                id="servicenow",
                display_name="ServiceNow",
                capabilities=["create", "update", "status"],
                supported=["incident"],
                requires_auth=True,
                configured=sn_configured,
                status="configured" if sn_configured else "missing_env",
                missing_env=sn_missing,
            ),
        )

        jira_missing = [env for env, val in {
            "JIRA_BASE_URL": self.settings.jira_base_url,
            "JIRA_EMAIL": self.settings.jira_email,
            "JIRA_API_TOKEN": self.settings.jira_api_token,
        }.items() if not val]
        jira_configured = self.settings.use_jirasm and not jira_missing
        self._maybe_add(
            "servicedesk",
            ServiceProvider(
                id="jira-sm",
                display_name="Jira Service Management",
                capabilities=["create", "comment", "status"],
                supported=["service-request"],
                requires_auth=True,
                configured=jira_configured,
                status="configured" if jira_configured else "missing_env",
                missing_env=jira_missing,
            ),
        )

        remedy_missing = [env for env, val in {
            "REMEDY_BASE_URL": self.settings.remedy_base_url,
            "REMEDY_USERNAME": self.settings.remedy_username,
            "REMEDY_PASSWORD": self.settings.remedy_password,
        }.items() if not val]
        remedy_configured = self.settings.use_remedy and not remedy_missing
        self._maybe_add(
            "servicedesk",
            ServiceProvider(
                id="remedy",
                display_name="BMC Remedy",
                capabilities=["create", "status"],
                supported=["incident"],
                requires_auth=True,
                configured=remedy_configured,
                status="configured" if remedy_configured else "missing_env",
                missing_env=remedy_missing,
            ),
        )

    def _maybe_add(self, key: str, provider: ServiceProvider) -> None:
        if provider.configured or self.settings.dev_mode:
            self.providers.setdefault(key, []).append(provider)

    def list_providers(self, include_unconfigured: bool = False) -> Dict[str, List[ServiceProvider]]:
        if include_unconfigured:
            return self.providers
        filtered: Dict[str, List[ServiceProvider]] = {}
        for key, items in self.providers.items():
            filtered[key] = [p for p in items if p.configured]
        return filtered

    def get_provider(self, service_type: str, provider_id: str) -> ServiceProvider:
        for provider in self.providers.get(service_type, []):
            if provider.id == provider_id:
                return provider
        raise ValueError(f"Provider {provider_id} not found for {service_type}")

    def is_configured(self, service_type: str, provider_id: str) -> bool:
        try:
            provider = self.get_provider(service_type, provider_id)
            return provider.configured
        except ValueError:
            return False

    def missing_env(self, service_type: str, provider_id: str) -> List[str]:
        provider = self.get_provider(service_type, provider_id)
        return provider.missing_env
