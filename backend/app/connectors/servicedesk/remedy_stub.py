from typing import Any, Dict

from .servicedesk_base import BaseServiceDeskConnector


class RemedyStub(BaseServiceDeskConnector):
    async def create_ticket(self, title: str, description: str) -> Dict[str, Any]:
        return {"id": "REMEDY-42", "title": title, "status": "logged", "notes": description}

    async def update_ticket(self, ticket_id: str, comment: str) -> Dict[str, Any]:
        return {"id": ticket_id, "comment": comment, "status": "work-in-progress"}

    async def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        return {"id": ticket_id, "status": "pending-customer"}
