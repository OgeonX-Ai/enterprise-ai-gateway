import uuid

from fastapi import APIRouter, Depends, Request

from ..integrations.servicenow.config import ServiceNowConfig
from ..integrations.servicenow.models import (
    AddWorkNoteRequest,
    NotifyResolverRequest,
    ScheduleFollowupRequest,
    SearchRequest,
    StandardToolResponse,
    TicketRequest,
    UpdateTicketRequest,
)
from ..integrations.servicenow.service import ServiceNowService
from ..settings import get_settings

router = APIRouter(prefix="/v1/tools/servicenow", tags=["tools"])


async def get_service() -> ServiceNowService:
    settings = get_settings()
    config = ServiceNowConfig.from_settings(settings)
    service = ServiceNowService(config)
    try:
        yield service
    finally:
        await service.shutdown()


def _correlation_id(request: Request) -> str:
    settings = getattr(getattr(request.app, "state", None), "settings", None)
    if settings:
        cid_header = settings.correlation_id_header
        return request.headers.get(cid_header) or str(uuid.uuid4())
    return request.headers.get("X-Correlation-ID") or str(uuid.uuid4())


@router.post("/search", response_model=StandardToolResponse)
async def search(request: Request, payload: SearchRequest, service: ServiceNowService = Depends(get_service)):
    correlation_id = _correlation_id(request)
    return await service.search(payload, correlation_id)


@router.post("/ticket/get", response_model=StandardToolResponse)
async def get_ticket(
    request: Request, payload: TicketRequest, service: ServiceNowService = Depends(get_service)
):
    correlation_id = _correlation_id(request)
    return await service.get_ticket(payload.ticket, correlation_id)


@router.post("/ticket/update", response_model=StandardToolResponse)
async def update_ticket(
    request: Request, payload: UpdateTicketRequest, service: ServiceNowService = Depends(get_service)
):
    correlation_id = _correlation_id(request)
    return await service.update_ticket(payload, correlation_id)


@router.post("/ticket/add_work_note", response_model=StandardToolResponse)
async def add_work_note(
    request: Request, payload: AddWorkNoteRequest, service: ServiceNowService = Depends(get_service)
):
    correlation_id = _correlation_id(request)
    return await service.add_work_note(payload, correlation_id)


@router.post("/notify_resolver", response_model=StandardToolResponse)
async def notify_resolver(
    request: Request, payload: NotifyResolverRequest, service: ServiceNowService = Depends(get_service)
):
    correlation_id = _correlation_id(request)
    return await service.notify_resolver(payload, correlation_id)


@router.post("/schedule_followup", response_model=StandardToolResponse)
async def schedule_followup(
    request: Request, payload: ScheduleFollowupRequest, service: ServiceNowService = Depends(get_service)
):
    correlation_id = _correlation_id(request)
    return await service.schedule_followup(payload, correlation_id)


@router.get("/capabilities", response_model=StandardToolResponse)
async def capabilities(service: ServiceNowService = Depends(get_service)):
    data = service.capabilities()
    return StandardToolResponse(ok=True, data=data)
