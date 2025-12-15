from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field("Enterprise AI Gateway", description="Application name")
    environment: str = Field("local", description="Deployment environment name")
    dev_mode: bool = Field(True, description="Expose debug data and unconfigured providers")
    correlation_id_header: str = Field("X-Correlation-ID", description="Header used for correlation IDs")

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
    servicenow_client_id: Optional[str] = Field(None, alias="SERVICENOW_CLIENT_ID")
    servicenow_client_secret: Optional[str] = Field(None, alias="SERVICENOW_CLIENT_SECRET")

    # Jira Service Management
    jira_base_url: Optional[str] = Field(None, alias="JIRA_BASE_URL")
    jira_email: Optional[str] = Field(None, alias="JIRA_EMAIL")
    jira_api_token: Optional[str] = Field(None, alias="JIRA_API_TOKEN")

    # Remedy
    remedy_base_url: Optional[str] = Field(None, alias="REMEDY_BASE_URL")
    remedy_username: Optional[str] = Field(None, alias="REMEDY_USERNAME")
    remedy_password: Optional[str] = Field(None, alias="REMEDY_PASSWORD")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
