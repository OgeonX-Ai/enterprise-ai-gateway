from typing import Any, Dict, List, Protocol


class LLMConnector(Protocol):
    async def generate(self, messages: List[Dict[str, str]], settings: Dict[str, Any]) -> str:
        ...


class SpeechConnector(Protocol):
    async def transcribe(self, audio_payload: bytes, settings: Dict[str, Any]) -> str:
        ...

    async def synthesize(self, text: str, settings: Dict[str, Any]) -> str:
        ...


class RAGConnector(Protocol):
    async def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        ...


class ServiceDeskConnector(Protocol):
    async def create_ticket(self, title: str, description: str) -> Dict[str, Any]:
        ...

    async def update_ticket(self, ticket_id: str, comment: str) -> Dict[str, Any]:
        ...

    async def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        ...
