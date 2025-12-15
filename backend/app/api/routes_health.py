from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz")
async def healthcheck() -> dict:
    return {"status": "ok"}
