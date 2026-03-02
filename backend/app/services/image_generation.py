import asyncio
import base64
import logging
from typing import List, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_HF_API_URL = (
    "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
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

        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    _HF_API_URL, headers=self.headers, json=payload
                )

                # Model can still be loading (503) — wait and retry once
                if response.status_code == 503:
                    logger.info("HuggingFace model loading — waiting 20 s and retrying.")
                    await asyncio.sleep(20)
                    response = await client.post(
                        _HF_API_URL, headers=self.headers, json=payload
                    )

                if response.status_code == 200:
                    return base64.b64encode(response.content).decode("utf-8")

                logger.error(
                    "Image generation failed [%s]: %s",
                    response.status_code,
                    response.text[:200],
                )
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
