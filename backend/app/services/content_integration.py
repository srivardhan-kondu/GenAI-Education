import asyncio
import logging
from datetime import datetime
from typing import List, Optional

from bson import ObjectId

from app.database.connection import get_database
from app.models.content import ContentRequest, ImageData, LearningModule, VideoData
from app.services.image_generation import image_generation_service
from app.services.text_generation import text_generation_service
from app.services.video_generation import video_generation_service
from app.services.voice_generation import voice_generation_service

logger = logging.getLogger(__name__)


class ContentIntegrationService:
    """
    Orchestrates the full content-generation pipeline:
      1. Text via OpenAI GPT
      2. Images (HuggingFace SD) + Audio (ElevenLabs) — concurrently
      3. Assembly into a LearningModule
      4. Persistence to MongoDB
    """

    async def generate_full_module(
        self,
        request: ContentRequest,
        user_id: str,
    ) -> LearningModule:

        # ── Step 1: Generate structured text ─────────────────────────────────
        logger.info("Generating text content for topic: '%s'", request.topic)
        text_content = await text_generation_service.generate_educational_content(
            request.topic,
            request.difficulty_level,
            request.explanation_style,
        )
        concepts = text_generation_service.extract_concepts(text_content)

        # ── Step 2: Generate images + audio concurrently ──────────────────────
        image_task = None
        audio_task = None
        video_task = None

        if request.generate_images and concepts:
            image_task = image_generation_service.generate_images_for_concepts(
                concepts, request.topic
            )
        if request.generate_audio:
            audio_task = voice_generation_service.generate_audio(
                topic=request.topic,
                definition=text_content.get("definition", ""),
                key_points=text_content.get("key_points", []),
                summary=text_content.get("summary", ""),
            )
        if request.generate_video and concepts:
            video_task = video_generation_service.generate_videos_for_concepts(
                concepts, request.topic
            )

        # Run whatever tasks exist in parallel
        coroutines = [t for t in (image_task, audio_task, video_task) if t is not None]
        raw_results = await asyncio.gather(*coroutines, return_exceptions=True)

        # Map results back
        result_iter = iter(raw_results)
        images_raw = next(result_iter) if image_task else []
        audio_b64 = next(result_iter) if audio_task else None
        videos_raw = next(result_iter) if video_task else []

        if isinstance(images_raw, Exception):
            logger.error("Image generation failed: %s", images_raw, exc_info=images_raw)
            images_raw = []
        if isinstance(audio_b64, Exception):
            logger.error("Audio generation failed: %s", audio_b64, exc_info=audio_b64)
            audio_b64 = None
        if isinstance(videos_raw, Exception):
            logger.error("Video generation failed: %s", videos_raw, exc_info=videos_raw)
            videos_raw = []

        # ── Step 3: Assemble module ───────────────────────────────────────────
        images = [
            ImageData(
                concept=img.get("concept", ""),
                base64_data=img.get("base64_data"),
            )
            for img in (images_raw or [])
        ]

        videos = [
            VideoData(
                concept=vid.get("concept", ""),
                base64_data=vid.get("base64_data"),
            )
            for vid in (videos_raw or [])
        ]

        module = LearningModule(
            user_id=user_id,
            topic=request.topic,
            difficulty_level=request.difficulty_level,
            definition=text_content.get("definition", ""),
            explanation=text_content.get("explanation", ""),
            examples=text_content.get("examples", []),
            key_points=text_content.get("key_points", []),
            summary=text_content.get("summary", ""),
            concepts=concepts,
            images=images,
            videos=videos,
            audio_base64=audio_b64,
            created_at=datetime.utcnow(),
        )

        # ── Step 4: Persist to MongoDB ────────────────────────────────────────
        return await self._save_module(module)

    # ── Persistence helpers ───────────────────────────────────────────────────

    async def _save_module(self, module: LearningModule) -> LearningModule:
        db = get_database()
        doc = module.model_dump(exclude={"id"})
        doc["images"] = [img.model_dump() for img in module.images]
        doc["videos"] = [vid.model_dump() for vid in module.videos]
        result = await db.learning_modules.insert_one(doc)
        module.id = str(result.inserted_id)
        return module

    async def get_user_history(self, user_id: str, limit: int = 30) -> List[dict]:
        db = get_database()
        cursor = (
            db.learning_modules.find(
                {"user_id": user_id},
                {"topic": 1, "difficulty_level": 1, "created_at": 1},
            )
            .sort("created_at", -1)
            .limit(limit)
        )
        history = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            if "created_at" in doc and hasattr(doc["created_at"], "isoformat"):
                doc["created_at"] = doc["created_at"].isoformat()
            history.append(doc)
        return history

    async def get_module_by_id(
        self, module_id: str, user_id: str
    ) -> Optional[dict]:
        db = get_database()
        try:
            doc = await db.learning_modules.find_one(
                {"_id": ObjectId(module_id), "user_id": user_id}
            )
        except Exception:
            return None

        if doc is None:
            return None

        doc["id"] = str(doc.pop("_id"))
        return doc

    async def search_modules(self, query: str, user_id: str) -> List[dict]:
        db = get_database()
        cursor = (
            db.learning_modules.find(
                {
                    "user_id": user_id,
                    "$or": [
                        {"topic": {"$regex": query, "$options": "i"}},
                        {
                            "concepts": {
                                "$elemMatch": {"$regex": query, "$options": "i"}
                            }
                        },
                    ],
                },
                {"topic": 1, "difficulty_level": 1, "created_at": 1},
            )
            .sort("created_at", -1)
            .limit(20)
        )
        results = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            if "created_at" in doc and hasattr(doc["created_at"], "isoformat"):
                doc["created_at"] = doc["created_at"].isoformat()
            results.append(doc)
        return results


content_integration_service = ContentIntegrationService()
