import logging
import time
from typing import Any, Dict, Optional

from fastapi import HTTPException

from ...common.logging import get_logger, log_event
from .client import ServiceNowClient
from .config import ServiceNowConfig
from .mock_store import MockIncidentStore
from .models import (
    AddWorkNoteRequest,
    NotifyResolverRequest,
    ScheduleFollowupRequest,
    SearchRequest,
    StandardToolResponse,
    TicketRef,
    UpdateTicketRequest,
)


class ServiceNowService:
    def __init__(self, config: ServiceNowConfig):
        self.config = config
        self.logger = get_logger(__name__)
        self.mock_store: Optional[MockIncidentStore] = None
        self.client: Optional[ServiceNowClient] = None
        if self.config.mock_mode:
            self.mock_store = MockIncidentStore()
        else:
            self.client = ServiceNowClient(config)

    async def shutdown(self):
        if self.client:
            await self.client.close()

    def _meta(self, start: float, correlation_id: str) -> Dict[str, Any]:
        return {
            "correlation_id": correlation_id,
            "mode": self.config.mode_label,
            "timing_ms": round((time.time() - start) * 1000, 2),
        }

    def _ensure_ticket(self, ticket: TicketRef):
        if not ticket.number and not ticket.sys_id:
            raise HTTPException(status_code=400, detail="ticket.number or ticket.sys_id required")

    async def search(self, payload: SearchRequest, correlation_id: str) -> StandardToolResponse:
        start = time.time()
        if self.config.mock_mode:
            results = self.mock_store.search(payload.query, payload.limit)
            log_event(
                self.logger,
                logging.INFO,
                "servicenow.search",
                "ServiceNow search (mock)",
                query=payload.query,
                correlation_id=correlation_id,
                mode="mock",
            )
            return StandardToolResponse(ok=True, data=results, meta=self._meta(start, correlation_id))

        try:
            log_event(
                self.logger,
                logging.INFO,
                "servicenow.search",
                "ServiceNow search",
                query=payload.query,
                correlation_id=correlation_id,
                mode="real",
            )
            response = await self.client.search_incidents(payload.query, payload.limit)
            return StandardToolResponse(ok=True, data=response, meta=self._meta(start, correlation_id))
        except Exception as exc:  # noqa: BLE001
            log_event(
                self.logger,
                logging.ERROR,
                "servicenow.search.failed",
                "ServiceNow search failed",
                correlation_id=correlation_id,
                exc_info=exc,
            )
            return StandardToolResponse(ok=False, error=str(exc), meta=self._meta(start, correlation_id))

    async def get_ticket(self, ticket: TicketRef, correlation_id: str) -> StandardToolResponse:
        start = time.time()
        self._ensure_ticket(ticket)
        if self.config.mock_mode:
            incident = self.mock_store.get(ticket.model_dump())
            if not incident:
                return StandardToolResponse(
                    ok=False, error="Ticket not found", meta=self._meta(start, correlation_id)
                )
            return StandardToolResponse(ok=True, data=incident, meta=self._meta(start, correlation_id))
        try:
            sys_id = ticket.sys_id or ticket.number
            response = await self.client.get_incident(sys_id)
            return StandardToolResponse(ok=True, data=response, meta=self._meta(start, correlation_id))
        except Exception as exc:  # noqa: BLE001
            log_event(
                self.logger,
                logging.ERROR,
                "servicenow.get_ticket.failed",
                "ServiceNow get ticket failed",
                correlation_id=correlation_id,
                exc_info=exc,
            )
            return StandardToolResponse(ok=False, error=str(exc), meta=self._meta(start, correlation_id))

    async def update_ticket(self, payload: UpdateTicketRequest, correlation_id: str) -> StandardToolResponse:
        start = time.time()
        self._ensure_ticket(payload.ticket)
        if self.config.mock_mode:
            incident = self.mock_store.update(payload.ticket.model_dump(), payload.fields, payload.reason)
            if not incident:
                return StandardToolResponse(
                    ok=False, error="Ticket not found", meta=self._meta(start, correlation_id)
                )
            return StandardToolResponse(ok=True, data=incident, meta=self._meta(start, correlation_id))
        try:
            sys_id = payload.ticket.sys_id or payload.ticket.number
            response = await self.client.update_incident(sys_id, payload.fields)
            return StandardToolResponse(ok=True, data=response, meta=self._meta(start, correlation_id))
        except Exception as exc:  # noqa: BLE001
            log_event(
                self.logger,
                logging.ERROR,
                "servicenow.update_ticket.failed",
                "ServiceNow update ticket failed",
                correlation_id=correlation_id,
                exc_info=exc,
            )
            return StandardToolResponse(ok=False, error=str(exc), meta=self._meta(start, correlation_id))

    async def add_work_note(self, payload: AddWorkNoteRequest, correlation_id: str) -> StandardToolResponse:
        start = time.time()
        self._ensure_ticket(payload.ticket)
        if self.config.mock_mode:
            incident = self.mock_store.add_work_note(
                payload.ticket.model_dump(), payload.note, payload.visibility
            )
            if not incident:
                return StandardToolResponse(
                    ok=False, error="Ticket not found", meta=self._meta(start, correlation_id)
                )
            return StandardToolResponse(ok=True, data=incident, meta=self._meta(start, correlation_id))
        try:
            sys_id = payload.ticket.sys_id or payload.ticket.number
            response = await self.client.add_work_note(sys_id, payload.note, payload.visibility)
            return StandardToolResponse(ok=True, data=response, meta=self._meta(start, correlation_id))
        except Exception as exc:  # noqa: BLE001
            log_event(
                self.logger,
                logging.ERROR,
                "servicenow.add_work_note.failed",
                "ServiceNow add work note failed",
                correlation_id=correlation_id,
                exc_info=exc,
            )
            return StandardToolResponse(ok=False, error=str(exc), meta=self._meta(start, correlation_id))

    async def notify_resolver(self, payload: NotifyResolverRequest, correlation_id: str) -> StandardToolResponse:
        start = time.time()
        self._ensure_ticket(payload.ticket)
        if self.config.mock_mode:
            data = self.mock_store.notify_resolver(
                payload.ticket.model_dump(), payload.message, payload.channel, payload.urgency
            )
            log_event(
                self.logger,
                logging.INFO,
                "servicenow.notify_resolver",
                "ServiceNow notify resolver (mock)",
                ticket=payload.ticket.model_dump(),
                correlation_id=correlation_id,
                mode="mock",
            )
            return StandardToolResponse(ok=True, data=data, meta=self._meta(start, correlation_id))
        try:
            sys_id = payload.ticket.sys_id or payload.ticket.number
            fields = {"comments": payload.message, "urgency": payload.urgency}
            response = await self.client.update_incident(sys_id, fields)
            return StandardToolResponse(ok=True, data=response, meta=self._meta(start, correlation_id))
        except Exception as exc:  # noqa: BLE001
            log_event(
                self.logger,
                logging.ERROR,
                "servicenow.notify_resolver.failed",
                "ServiceNow notify resolver failed",
                correlation_id=correlation_id,
                exc_info=exc,
            )
            return StandardToolResponse(ok=False, error=str(exc), meta=self._meta(start, correlation_id))

    async def schedule_followup(self, payload: ScheduleFollowupRequest, correlation_id: str) -> StandardToolResponse:
        start = time.time()
        self._ensure_ticket(payload.ticket)
        log_event(
            self.logger,
            logging.INFO,
            "servicenow.schedule_followup",
            "ServiceNow schedule_followup stub",
            ticket=payload.ticket.model_dump(),
            with_party=payload.with_party,
            correlation_id=correlation_id,
        )
        return StandardToolResponse(
            ok=True,
            data={
                "status": "queued",
                "message": f"Follow-up proposed with {payload.with_party}",
                "proposed_times": payload.proposed_times,
            },
            meta=self._meta(start, correlation_id),
        )

    def capabilities(self) -> Dict[str, Any]:
        return {
            "mode": self.config.mode_label,
            "instance_url": self.config.instance_url,
            "auth_mode": self.config.auth_mode,
            "supports": [
                "search",
                "get",
                "update",
                "add_work_note",
                "notify_resolver",
                "schedule_followup",
            ],
        }
