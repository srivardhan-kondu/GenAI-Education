from fastapi import APIRouter, Depends, Query

from app.services.content_integration import content_integration_service
from app.utils.auth_utils import get_current_user
from app.utils.validators import _INVALID_CHARS

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/")
async def search_content(
    q: str = Query(..., min_length=1, max_length=100),
    current_user: dict = Depends(get_current_user),
):
    # Sanitise query
    q = q.strip()
    if _INVALID_CHARS.search(q):
        return {"results": []}

    results = await content_integration_service.search_modules(q, current_user["id"])
    return {"results": results}
