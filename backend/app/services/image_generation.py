import asyncio
import base64
import logging
from typing import List, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_HF_API_URL = (
    "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
)


class ImageGenerationService:
    def __init__(self) -> None:
        self.headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}

    async def generate_image(self, concept: str, topic: str) -> Optional[str]:
        """
        Call Hugging Face Inference API to generate an educational illustration.
        Returns the image as a base64-encoded string, or None on failure.
        """
        if not settings.HUGGINGFACE_API_KEY:
            logger.warning("HUGGINGFACE_API_KEY not set — skipping image generation.")
            return None

        prompt = (
            f"Educational diagram illustrating '{concept}' as part of {topic}. "
            "Clean infographic style, white background, clearly labelled, "
            "suitable for students, high quality."
        )
        payload = {
            "inputs": prompt,
            "parameters": {"num_inference_steps": 25, "guidance_scale": 7.5},
        }

        max_retries = 3
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                for attempt in range(max_retries):
                    response = await client.post(
                        _HF_API_URL, headers=self.headers, json=payload
                    )

                    if response.status_code == 200:
                        return base64.b64encode(response.content).decode("utf-8")

                    # Model can still be loading (503) — wait and retry
                    if response.status_code == 503:
                        wait = 20 * (attempt + 1)
                        logger.info(
                            "HuggingFace model loading (attempt %d/%d) — waiting %ds.",
                            attempt + 1, max_retries, wait,
                        )
                        await asyncio.sleep(wait)
                        continue

                    logger.error(
                        "Image generation failed [%s]: %s",
                        response.status_code,
                        response.text[:200],
                    )
                    return None

                logger.error("Image generation failed after %d retries (503).", max_retries)
                return None

        except Exception:
            logger.exception("Image generation error for concept '%s'", concept)
            return None

    async def generate_images_for_concepts(
        self, concepts: List[str], topic: str
    ) -> List[dict]:
        """Generate images for up to 3 concepts concurrently."""
        subset = concepts[:3]
        tasks = [self.generate_image(c, topic) for c in subset]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        images = []
        for concept, result in zip(subset, results):
            b64 = result if isinstance(result, str) else None
            images.append({"concept": concept, "base64_data": b64})

        return images


image_generation_service = ImageGenerationService()
