from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class ProviderSelection(BaseModel):
    llm_provider: str
    llm_model: str
    rag_provider: Optional[str] = None
    rag_index: Optional[str] = None
    stt_provider: Optional[str] = None
    stt_model: Optional[str] = None
    tts_provider: Optional[str] = None
    tts_voice: Optional[str] = None
    servicedesk_provider: Optional[str] = None


class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Existing session identifier")
    channel: str = Field(..., description="Request channel such as web, teams, ivr")
    message: str = Field(..., description="User message content")
    provider_selection: ProviderSelection
    use_rag: bool = False
    include_debug: bool = False


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    providers: ProviderSelection
    used_rag: bool
    servicedesk_action: Optional[str]
    debug: Optional[Dict[str, Any]] = None


class SessionResponse(BaseModel):
    session_id: str


class RegistryItem(BaseModel):
    id: str
    display_name: str
    capabilities: List[str]
    supported: List[str]
    requires_auth: bool
    status: str
    configured: bool
    missing_env: List[str] = []


class RegistryResponse(BaseModel):
    llm: List[RegistryItem]
    rag: List[RegistryItem]
    stt: List[RegistryItem]
    tts: List[RegistryItem]
    servicedesk: List[RegistryItem]


class ValidationDetail(BaseModel):
    service_type: str
    provider: str
    status: str
    reason: str


class ValidationResponse(BaseModel):
    status: str
    results: List[ValidationDetail]
