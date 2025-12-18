from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from ..services import whisper_service

router = APIRouter(prefix="/api/whisper")


@router.get("/config")
async def whisper_config() -> dict:
    return {
        "models": ["tiny", "small", "medium"],
        "defaults": {
            "model": "small",
            "language": "auto",
            "beam_size": 1,
            "chunk_length": 4,
            "vad_filter": True,
            "compute_type": "int8",
        },
        "notes": {
            "cpu": "All models run on CPU only. Medium may be slow on laptops.",
            "audio": "Prefer WAV/PCM uploads. Browser recorder will convert to mono 16k.",
        },
    }


@router.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    settings: str | None = Form(None),
) -> dict:
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty audio payload",
        )

    parsed_settings = whisper_service.parse_settings(settings)
    try:
        result = whisper_service.transcribe_audio(audio_bytes, parsed_settings)
    except Exception as exc:  # pragma: no cover - defensive guard for demo inputs
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to transcribe audio: {exc}",
        ) from exc
    result["filename"] = file.filename
    return result
