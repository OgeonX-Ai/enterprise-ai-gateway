import base64
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
    locale = body.get("locale", "en-US")
    model = body.get("model", "default")
    audio_bytes = base64.b64decode(body.get("audio_base64", "")) if body.get("audio_base64") else b""
    transcript = await runtime.transcribe_audio(provider_id, audio_bytes, locale=locale, model=model)
    return transcript


@router.post("/synthesize")
async def synthesize(
    payload: dict,
    runtime: AgentRuntime = Depends(get_runtime),
) -> dict:
    provider_id = payload.get("tts_provider", "mock-tts")
    voice = payload.get("voice", "alloy")
    locale = payload.get("locale", "en-US")
    result = await runtime.synthesize_audio(provider_id, payload.get("text", ""), locale=locale, voice=voice)
    audio_base64 = base64.b64encode(result.get("audio", b"")) if result.get("audio") else b""
    return {"audio_base64": audio_base64.decode(), "latency_ms": result.get("latency_ms")}
