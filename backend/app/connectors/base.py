from typing import Any, Dict, List, Protocol


class LLMConnector(Protocol):
    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 256,
    ) -> Dict[str, Any]:
        ...


class STTConnector(Protocol):
    async def transcribe(self, audio_payload: bytes, locale: str, model: str) -> Dict[str, Any]:
        ...


class TTSConnector(Protocol):
    async def synthesize(self, text: str, locale: str, voice: str) -> Dict[str, Any]:
        ...


class RAGConnector(Protocol):
    async def search(self, query: str, top_k: int, index_name: str) -> List[Dict[str, Any]]:
        ...


class ServiceDeskConnector(Protocol):
    async def create_ticket(self, title: str, body: str, severity: str, requester: str | None = None) -> Dict[str, Any]:
        ...

    async def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        ...

    async def search_kb(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        ...

    async def validate(self) -> Dict[str, Any]:
        ...
