from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field("enterprise-ai-gateway", alias="APP_NAME", description="Application name")
    app_version: str = Field("0.1.0", alias="APP_VERSION", description="Application version")
    build_sha: Optional[str] = Field(None, alias="BUILD_COMMIT", description="Build commit SHA")
    environment: str = Field("local", description="Deployment environment name")
    stt_provider: str = Field("local_whisper", alias="STT_PROVIDER")
    stt_default_model: str = Field("tiny", alias="STT_DEFAULT_MODEL")
    stt_default_language: str = Field("fi", alias="STT_DEFAULT_LANGUAGE")
    stt_whisper_compute_type: str = Field("int8", alias="STT_WHISPER_COMPUTE_TYPE")
    hardware_hint: str = Field("Lenovo T480 (CPU)", alias="HARDWARE_HINT")
    dev_mode: bool = Field(True, description="Expose debug data and unconfigured providers")
    correlation_id_header: str = Field("X-Correlation-ID", description="Header used for correlation IDs")
    enable_debug_stream: bool = Field(True, alias="ENABLE_DEBUG_STREAM", description="Enable SSE debug stream")

    # Feature flags
    use_azure_openai: bool = Field(False, alias="USE_AZURE_OPENAI")
    use_azure_speech: bool = Field(False, alias="USE_AZURE_SPEECH")
    use_azure_search: bool = Field(False, alias="USE_AZURE_SEARCH")
    use_servicenow: bool = Field(False, alias="USE_SERVICENOW")
    use_jirasm: bool = Field(False, alias="USE_JIRASM")
    use_remedy: bool = Field(False, alias="USE_REMEDY")

    # Azure OpenAI
    azure_openai_endpoint: Optional[str] = Field(None, alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: Optional[str] = Field(None, alias="AZURE_OPENAI_API_KEY")
    azure_openai_api_version: Optional[str] = Field("2024-02-15-preview", alias="AZURE_OPENAI_API_VERSION")
    azure_openai_deployments: List[str] = Field(default_factory=list, alias="AZURE_OPENAI_DEPLOYMENTS")

    # Azure Speech
    azure_speech_key: Optional[str] = Field(None, alias="AZURE_SPEECH_KEY")
    azure_speech_region: Optional[str] = Field(None, alias="AZURE_SPEECH_REGION")

    # Azure AI Search
    azure_search_endpoint: Optional[str] = Field(None, alias="AZURE_SEARCH_ENDPOINT")
    azure_search_query_key: Optional[str] = Field(None, alias="AZURE_SEARCH_QUERY_KEY")
    azure_search_index_default: Optional[str] = Field(None, alias="AZURE_SEARCH_INDEX_DEFAULT")

    # ServiceNow
    servicenow_instance_url: Optional[str] = Field(None, alias="SERVICENOW_INSTANCE_URL")
    servicenow_auth_mode: str = Field("basic", alias="SERVICENOW_AUTH_MODE")
    servicenow_username: Optional[str] = Field(None, alias="SERVICENOW_USERNAME")
    servicenow_password: Optional[str] = Field(None, alias="SERVICENOW_PASSWORD")
    servicenow_client_id: Optional[str] = Field(None, alias="SERVICENOW_CLIENT_ID")
    servicenow_client_secret: Optional[str] = Field(None, alias="SERVICENOW_CLIENT_SECRET")
    servicenow_token_url: Optional[str] = Field(None, alias="SERVICENOW_TOKEN_URL")
    servicenow_mock_mode: bool = Field(True, alias="SERVICENOW_MOCK_MODE")

    cors_allow_origins: str = Field(
        "https://ogeonx-ai.github.io,http://127.0.0.1:5500,http://localhost:5500",
        alias="CORS_ALLOW_ORIGINS",
    )

    # Jira Service Management
    jira_base_url: Optional[str] = Field(None, alias="JIRA_BASE_URL")
    jira_email: Optional[str] = Field(None, alias="JIRA_EMAIL")
    jira_api_token: Optional[str] = Field(None, alias="JIRA_API_TOKEN")

    # Remedy
    remedy_base_url: Optional[str] = Field(None, alias="REMEDY_BASE_URL")
    remedy_username: Optional[str] = Field(None, alias="REMEDY_USERNAME")
    remedy_password: Optional[str] = Field(None, alias="REMEDY_PASSWORD")

    # ElevenLabs
    elevenlabs_api_key: Optional[str] = Field(None, alias="ELEVENLABS_API_KEY")
    elevenlabs_model_id: str = Field("eleven_multilingual_v2", alias="ELEVENLABS_MODEL_ID")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
