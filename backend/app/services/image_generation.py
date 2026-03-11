import asyncio
import base64
import io
import logging
from typing import List, Optional

import httpx
from PIL import Image

from app.config import settings

logger = logging.getLogger(__name__)

_OPENAI_IMG_URL = "https://api.openai.com/v1/images/generations"
_MAX_IMAGE_SIZE = 512  # resize to this max dimension to keep MongoDB docs small


class ImageGenerationService:
    def __init__(self) -> None:
        self.api_key = settings.OPENAI_API_KEY

    async def generate_image(self, concept: str, topic: str) -> Optional[str]:
        """
        Call OpenAI DALL-E to generate an educational illustration.
        Returns the image as a base64-encoded string, or None on failure.
        """
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set — skipping image generation.")
            return None

        prompt = (
            f"Educational diagram illustrating '{concept}' as part of {topic}. "
            "Clean infographic style, white background, clearly labelled, "
            "suitable for students, high quality."
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
            "response_format": "b64_json",
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    _OPENAI_IMG_URL, headers=headers, json=payload
                )

                if response.status_code == 200:
                    data = response.json()
                    raw_b64 = data["data"][0]["b64_json"]
                    return self._compress_image(raw_b64)

                # If DALL-E 3 fails (e.g. billing/access issue), fall back to DALL-E 2
                logger.warning(
                    "DALL-E 3 failed [%s], trying DALL-E 2 fallback...",
                    response.status_code,
                )
                payload["model"] = "dall-e-2"
                payload["size"] = "512x512"

                response = await client.post(
                    _OPENAI_IMG_URL, headers=headers, json=payload
                )

                if response.status_code == 200:
                    data = response.json()
                    raw_b64 = data["data"][0]["b64_json"]
                    return self._compress_image(raw_b64)

                logger.error(
                    "Image generation failed [%s]: %s",
                    response.status_code,
                    response.text[:300],
                )
                return None

        except Exception:
            logger.exception("Image generation error for concept '%s'", concept)
            return None

    @staticmethod
    def _compress_image(b64_data: str) -> str:
        """Resize and compress a base64 image to JPEG to fit within MongoDB limits."""
        raw = base64.b64decode(b64_data)
        img = Image.open(io.BytesIO(raw)).convert("RGB")
        img.thumbnail((_MAX_IMAGE_SIZE, _MAX_IMAGE_SIZE), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80, optimize=True)
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    async def generate_images_for_concepts(
        self, concepts: List[str], topic: str
    ) -> List[dict]:
        """Generate images for up to 3 concepts (sequentially — DALL-E rate limits)."""
        subset = concepts[:3]
        images = []
        for concept in subset:
            b64 = await self.generate_image(concept, topic)
            images.append({"concept": concept, "base64_data": b64})
        return images


image_generation_service = ImageGenerationService()
