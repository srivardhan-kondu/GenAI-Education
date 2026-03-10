import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response

from app.services.content_integration import content_integration_service
from app.services.notes_generation import notes_generation_service
from app.services.pdf_export import pdf_export_service
from app.utils.auth_utils import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/notes", tags=["Notes"])

VALID_FORMATS = {"structured", "cornell", "flashcards"}


# ── Generate Notes (JSON) ────────────────────────────────────────────────────

@router.get("/{module_id}")
async def generate_notes(
    module_id: str,
    format: str = Query(default="structured", description="structured | cornell | flashcards"),
    current_user: dict = Depends(get_current_user),
):
    """Generate study notes from an existing learning module."""
    if format not in VALID_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"format must be one of: {', '.join(VALID_FORMATS)}",
        )

    module = await content_integration_service.get_module_by_id(
        module_id, current_user["id"]
    )
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found.")

    try:
        if format == "structured":
            notes = notes_generation_service.generate_structured_notes(module)
        elif format == "cornell":
            notes = await notes_generation_service.generate_cornell_notes(module)
        else:  # flashcards
            notes = await notes_generation_service.generate_flashcards(module)
    except Exception as exc:
        logger.exception("Notes generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Notes generation failed: {exc}",
        )

    return notes


# ── Download Notes as PDF ─────────────────────────────────────────────────────

@router.get("/{module_id}/pdf")
async def download_notes_pdf(
    module_id: str,
    format: str = Query(default="structured", description="structured | cornell | flashcards"),
    current_user: dict = Depends(get_current_user),
):
    """Download study notes as a PDF file."""
    if format not in VALID_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"format must be one of: {', '.join(VALID_FORMATS)}",
        )

    module = await content_integration_service.get_module_by_id(
        module_id, current_user["id"]
    )
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found.")

    try:
        if format == "structured":
            notes = notes_generation_service.generate_structured_notes(module)
            pdf_bytes = pdf_export_service.generate_structured_pdf(notes)
        elif format == "cornell":
            notes = await notes_generation_service.generate_cornell_notes(module)
            pdf_bytes = pdf_export_service.generate_cornell_pdf(notes)
        else:
            notes = await notes_generation_service.generate_flashcards(module)
            pdf_bytes = pdf_export_service.generate_flashcards_pdf(notes)
    except Exception as exc:
        logger.exception("PDF notes generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF generation failed: {exc}",
        )

    safe_topic = module.get("topic", "notes").replace(" ", "_")[:30]
    filename = f"EduGen_{safe_topic}_{format}_notes.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
