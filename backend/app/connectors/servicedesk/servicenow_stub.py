from typing import Any, Dict

from .servicedesk_base import BaseServiceDeskConnector


class ServiceNowStub(BaseServiceDeskConnector):
    async def create_ticket(self, title: str, description: str) -> Dict[str, Any]:
        return {"id": "SNOW-1001", "title": title, "description": description, "status": "new"}

    async def update_ticket(self, ticket_id: str, comment: str) -> Dict[str, Any]:
        return {"id": ticket_id, "comment": comment, "status": "updated"}

    async def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        return {"id": ticket_id, "status": "in-progress"}
