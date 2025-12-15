from typing import Any, Dict, Protocol


class BaseServiceDeskConnector(Protocol):
    async def create_ticket(self, title: str, description: str) -> Dict[str, Any]:
        ...

    async def update_ticket(self, ticket_id: str, comment: str) -> Dict[str, Any]:
        ...

    async def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        ...
