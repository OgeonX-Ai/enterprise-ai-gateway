from fastapi import APIRouter, Depends, Request

from ..runtime.agent_runtime import AgentRuntime

router = APIRouter(prefix="/v1/audio")


def get_runtime(request: Request) -> AgentRuntime:
    return request.app.state.runtime


@router.post("/transcribe")
async def transcribe(
    request: Request,
    runtime: AgentRuntime = Depends(get_runtime),
) -> dict:
    body = await request.json()
    provider_id = body.get("stt_provider", "mock-stt")
    transcript = await runtime.transcribe_audio(provider_id, b"")
    return {"text": transcript}


@router.post("/synthesize")
async def synthesize(
    payload: dict,
    runtime: AgentRuntime = Depends(get_runtime),
) -> dict:
    provider_id = payload.get("tts_provider", "mock-tts")
    voice = payload.get("voice")
    audio = await runtime.synthesize_audio(provider_id, payload.get("text", ""), voice)
    return {"audio": audio}
