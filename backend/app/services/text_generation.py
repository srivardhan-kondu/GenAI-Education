import json
import logging
import re
from typing import Dict, List

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_DIFFICULTY_GUIDE = {
    "beginner": "simple, jargon-free language with helpful analogies",
    "intermediate": "moderate technical depth with some domain terminology",
    "advanced": "technical precision, full domain terminology, and nuanced details",
}

_STYLE_GUIDE = {
    "short": "concise and brief — each section 1–3 sentences",
    "detailed": "comprehensive and thorough — each section well-developed",
}

# OpenAI config
_OPENAI_URL = "https://api.openai.com/v1/chat/completions"
_MODEL = "gpt-4o-mini"


class TextGenerationService:
    def __init__(self) -> None:
        self.api_key = settings.OPENAI_API_KEY

    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI Chat Completions API via httpx."""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": _MODEL,
            "messages": [
                {"role": "system", "content": "You are an expert educational content creator. Always return valid JSON only — no markdown fences, no extra commentary."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 4096,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                resp = await client.post(_OPENAI_URL, headers=headers, json=payload)
                data = resp.json()

                if resp.status_code == 200:
                    text = data["choices"][0]["message"]["content"]
                    logger.info("✅ OpenAI %s succeeded", _MODEL)
                    return text.strip()

                err_msg = data.get("error", {}).get("message", str(data))
                raise ValueError(f"OpenAI API error {resp.status_code}: {err_msg}")

            except httpx.TimeoutException:
                raise ValueError(f"OpenAI API request timed out after 60s")

    async def generate_educational_content(
        self,
        topic: str,
        difficulty_level: str = "beginner",
        explanation_style: str = "detailed",
    ) -> Dict:
        prompt = f"""Generate structured learning content about "{topic}" for a {difficulty_level} learner.

Guidelines:
- Language style: {_DIFFICULTY_GUIDE.get(difficulty_level, 'clear')}
- Length style:   {_STYLE_GUIDE.get(explanation_style, 'comprehensive')}
- Return ONLY valid JSON — no markdown fences, no extra commentary.

Required JSON structure (all fields mandatory):
{{
  "definition":  "<1-2 sentence clear definition of {topic}>",
  "explanation": "<thorough concept explanation>",
  "examples":    ["<concrete example 1>", "<concrete example 2>", "<concrete example 3>"],
  "key_points":  ["<key point 1>", "<key point 2>", "<key point 3>", "<key point 4>", "<key point 5>"],
  "summary":     "<brief wrap-up of what was learned>",
  "concepts":    ["<visual concept 1>", "<visual concept 2>", "<visual concept 3>"]
}}

The "concepts" array must contain 2-4 specific, concrete sub-topics of "{topic}" that would benefit from a diagram or illustration.
"""

        raw = await self._call_openai(prompt)

        # Strip any accidental markdown code fences
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Try to salvage embedded JSON
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                except json.JSONDecodeError:
                    data = self._fallback(topic, raw)
            else:
                data = self._fallback(topic, raw)

        return data

    def extract_concepts(self, content: Dict) -> List[str]:
        return content.get("concepts", [])

    @staticmethod
    def _fallback(topic: str, raw_text: str) -> Dict:
        logger.warning("Falling back to minimal content structure for topic: %s", topic)
        return {
            "definition": f"{topic} is an important concept.",
            "explanation": raw_text[:600] if raw_text else f"Learn about {topic}.",
            "examples": [f"Example of {topic} in real life."],
            "key_points": [f"Understanding {topic} is essential."],
            "summary": f"This module introduced key ideas about {topic}.",
            "concepts": [topic],
        }


text_generation_service = TextGenerationService()
