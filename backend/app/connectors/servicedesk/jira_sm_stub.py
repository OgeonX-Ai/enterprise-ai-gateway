from typing import Any, Dict

from .servicedesk_base import BaseServiceDeskConnector


class JiraServiceManagementStub(BaseServiceDeskConnector):
    async def create_ticket(self, title: str, description: str) -> Dict[str, Any]:
        return {"id": "JIRA-9000", "summary": title, "description": description, "status": "open"}

    async def update_ticket(self, ticket_id: str, comment: str) -> Dict[str, Any]:
        return {"id": ticket_id, "comment": comment, "status": "commented"}

    async def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        return {"id": ticket_id, "status": "triage"}
