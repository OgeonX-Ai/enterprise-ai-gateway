from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search keywords")
    limit: int = Field(5, description="Maximum results to return")


class TicketRef(BaseModel):
    number: Optional[str] = Field(None, description="Incident number")
    sys_id: Optional[str] = Field(None, description="ServiceNow sys_id")


class TicketRequest(BaseModel):
    ticket: TicketRef


class UpdateTicketRequest(BaseModel):
    ticket: TicketRef
    fields: Dict[str, Any]
    reason: str


class AddWorkNoteRequest(BaseModel):
    ticket: TicketRef
    note: str
    visibility: Literal["internal", "public"] = "internal"


class NotifyResolverRequest(BaseModel):
    ticket: TicketRef
    message: str
    channel: Literal["email", "teams", "phone"] = "email"
    urgency: Literal["low", "normal", "high"] = "normal"


class ScheduleFollowupRequest(BaseModel):
    ticket: TicketRef
    with_party: str
    purpose: str
    proposed_times: List[str]


class StandardToolResponse(BaseModel):
    ok: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
