import json
import logging
import re
from typing import Dict

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# OpenAI config
_OPENAI_URL = "https://api.openai.com/v1/chat/completions"
_MODEL = "gpt-4o-mini"


class NotesGenerationService:
    """
    Generates structured study notes from an existing learning module.
    Three modes:
      1. Structured Notes — reformats module data (no API call)
      2. Cornell Notes  — uses OpenAI GPT to create Cues | Notes | Summary
      3. Flashcards     — uses OpenAI GPT to create Q&A pairs
    """

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
                {"role": "system", "content": "You are an expert study-skills tutor. Always return valid JSON only — no markdown fences, no extra commentary."},
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
                raise ValueError("OpenAI API request timed out after 60s")

    # ── Mode 1: Structured study notes (no AI call) ──────────────────────────

    def generate_structured_notes(self, module: dict) -> dict:
        """Reformat existing module content into clean study notes."""
        topic = module.get("topic", "Untitled")
        return {
            "type": "structured",
            "topic": topic,
            "difficulty_level": module.get("difficulty_level", "beginner"),
            "sections": [
                {"heading": "📘 Definition", "content": module.get("definition", "")},
                {"heading": "📖 Detailed Explanation", "content": module.get("explanation", "")},
                {"heading": "💡 Examples", "items": module.get("examples", [])},
                {"heading": "🔑 Key Points", "items": module.get("key_points", [])},
                {"heading": "🧠 Core Concepts", "items": module.get("concepts", [])},
                {"heading": "📝 Summary", "content": module.get("summary", "")},
            ],
        }

    # ── Mode 2: AI-powered Cornell Notes ─────────────────────────────────────

    async def generate_cornell_notes(self, module: dict) -> dict:
        """Use OpenAI GPT to reformat module content into Cornell Notes format."""
        topic = module.get("topic", "")
        definition = module.get("definition", "")
        explanation = module.get("explanation", "")
        examples = module.get("examples", [])
        key_points = module.get("key_points", [])
        summary = module.get("summary", "")

        source_text = (
            f"Topic: {topic}\n"
            f"Definition: {definition}\n"
            f"Explanation: {explanation}\n"
            f"Examples: {'; '.join(examples)}\n"
            f"Key Points: {'; '.join(key_points)}\n"
            f"Summary: {summary}"
        )

        prompt = f"""Convert the following educational content into **Cornell Notes** format.

Source content:
{source_text}

Return ONLY valid JSON with this structure:
{{
  "cue_column": [
    {{ "cue": "<question or keyword>", "notes": "<detailed notes answering/explaining the cue>" }}
  ],
  "summary": "<2-3 sentence summary of the entire topic for quick revision>"
}}

Rules:
- Create 5-8 cue/notes pairs.
- Cues should be short questions or keywords (like a student would write in the left margin).
- Notes should be concise but informative (right-side detailed notes).
- The summary should capture the essence of the topic for quick review.
- Return ONLY valid JSON — no markdown fences, no extra commentary.
"""

        try:
            raw = await self._call_openai(prompt)
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                match = re.search(r"\{.*\}", raw, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                else:
                    data = self._cornell_fallback(module)

        except Exception:
            logger.exception("Cornell Notes generation failed for topic: %s", topic)
            data = self._cornell_fallback(module)

        return {
            "type": "cornell",
            "topic": topic,
            "difficulty_level": module.get("difficulty_level", "beginner"),
            "cue_column": data.get("cue_column", []),
            "summary": data.get("summary", summary),
        }

    @staticmethod
    def _cornell_fallback(module: dict) -> dict:
        """Fallback if OpenAI fails — create basic Cornell Notes from existing data."""
        cues = []
        if module.get("definition"):
            cues.append({
                "cue": f"What is {module['topic']}?",
                "notes": module["definition"],
            })
        for i, kp in enumerate(module.get("key_points", [])[:6]):
            cues.append({
                "cue": f"Key Point {i + 1}",
                "notes": kp,
            })
        return {
            "cue_column": cues,
            "summary": module.get("summary", ""),
        }

    # ── Mode 3: Flashcards ───────────────────────────────────────────────────

    async def generate_flashcards(self, module: dict) -> dict:
        """Use OpenAI GPT to generate Q&A flashcards from module content."""
        topic = module.get("topic", "")
        definition = module.get("definition", "")
        explanation = module.get("explanation", "")
        key_points = module.get("key_points", [])

        source_text = (
            f"Topic: {topic}\nDefinition: {definition}\n"
            f"Explanation: {explanation}\n"
            f"Key Points: {'; '.join(key_points)}"
        )

        prompt = f"""Generate 8 study flashcards (question/answer pairs) from this educational content.

Source content:
{source_text}

Return ONLY valid JSON:
{{
  "flashcards": [
    {{ "question": "<question>", "answer": "<concise answer>" }}
  ]
}}

Rules:
- Mix factual recall, conceptual understanding, and application questions.
- Answers should be 1-3 sentences.
- Return ONLY valid JSON — no markdown fences, no extra commentary.
"""

        try:
            raw = await self._call_openai(prompt)
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            data = json.loads(raw)
        except Exception:
            logger.exception("Flashcard generation failed for topic: %s", topic)
            data = {"flashcards": [
                {"question": f"What is {topic}?", "answer": definition or f"{topic} is an important concept."},
            ]}

        return {
            "type": "flashcards",
            "topic": topic,
            "flashcards": data.get("flashcards", []),
        }


notes_generation_service = NotesGenerationService()
