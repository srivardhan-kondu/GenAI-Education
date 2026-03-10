import base64
import logging
from typing import List, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_EL_BASE_URL = "https://api.elevenlabs.io/v1"
_MAX_CHARS = 2500  # stay comfortably within free-tier monthly limit per call


class VoiceGenerationService:
    def _build_narration(
        self,
        topic: str,
        definition: str,
        key_points: List[str],
        summary: str,
    ) -> str:
        points_text = "  ".join(f"{i + 1}. {p}" for i, p in enumerate(key_points[:4]))
        text = (
            f"Welcome to this learning module about {topic}.\n\n"
            f"{definition}\n\n"
            f"Here are the key points you should remember.\n{points_text}\n\n"
            f"In summary: {summary}\n\n"
            f"Thank you for learning about {topic} with EduGen AI."
        )
        return text[:_MAX_CHARS]

    async def generate_audio(
        self,
        topic: str,
        definition: str,
        key_points: List[str],
        summary: str,
    ) -> Optional[str]:
        """Convert text to speech using ElevenLabs. Returns base64-encoded MP3."""
        if not settings.ELEVENLABS_API_KEY:
            logger.warning("ELEVENLABS_API_KEY not set — skipping voice generation.")
            return None

        narration = self._build_narration(topic, definition, key_points, summary)

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": settings.ELEVENLABS_API_KEY,
        }
        payload = {
            "text": narration,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }

        url = f"{_EL_BASE_URL}/text-to-speech/{settings.ELEVENLABS_VOICE_ID}"
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                return base64.b64encode(response.content).decode("utf-8")

            logger.error(
                "Voice generation failed [%s]: %s",
                response.status_code,
                response.text[:200],
            )
            return None

        except Exception:
            logger.exception("Voice generation error for topic '%s'", topic)
            return None


voice_generation_service = VoiceGenerationService()
