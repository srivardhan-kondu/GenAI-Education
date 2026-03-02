import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.content import ContentRequest
from app.services.content_integration import content_integration_service
from app.utils.auth_utils import get_current_user
from app.utils.validators import validate_difficulty, validate_style, validate_topic

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/content", tags=["Content"])


# ── Generate ──────────────────────────────────────────────────────────────────

@router.post("/generate")
async def generate_content(
    request: ContentRequest,
    current_user: dict = Depends(get_current_user),
):
    request.topic = validate_topic(request.topic)
    request.difficulty_level = validate_difficulty(request.difficulty_level)
    request.explanation_style = validate_style(request.explanation_style)

    try:
        module = await content_integration_service.generate_full_module(
            request, current_user["id"]
        )
    except Exception as exc:
        logger.exception("Content generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {exc}",
        )

    return {
        "id": module.id,
        "topic": module.topic,
        "difficulty_level": module.difficulty_level,
        "definition": module.definition,
        "explanation": module.explanation,
        "examples": module.examples,
        "key_points": module.key_points,
        "summary": module.summary,
        "concepts": module.concepts,
        "images": [img.model_dump() for img in module.images],
        "audio_base64": module.audio_base64,
        "created_at": module.created_at.isoformat(),
    }


# ── History ───────────────────────────────────────────────────────────────────

@router.get("/history")
async def get_history(current_user: dict = Depends(get_current_user)):
    history = await content_integration_service.get_user_history(current_user["id"])
    return {"history": history}


# ── Get by ID ─────────────────────────────────────────────────────────────────

@router.get("/{module_id}")
async def get_module(
    module_id: str,
    current_user: dict = Depends(get_current_user),
):
    module = await content_integration_service.get_module_by_id(
        module_id, current_user["id"]
    )
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found.")

    # Ensure created_at is JSON-serialisable
    if "created_at" in module and hasattr(module["created_at"], "isoformat"):
        module["created_at"] = module["created_at"].isoformat()

    return module
