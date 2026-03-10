from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ContentRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200)
    difficulty_level: str = Field(default="beginner")
    explanation_style: str = Field(default="detailed")
    generate_images: bool = True
    generate_audio: bool = True
    generate_video: bool = False  # opt-in (slower)


class ImageData(BaseModel):
    concept: str
    base64_data: Optional[str] = None  # base64-encoded PNG/JPEG


class VideoData(BaseModel):
    concept: str
    base64_data: Optional[str] = None  # base64-encoded MP4


class LearningModule(BaseModel):
    id: Optional[str] = None
    user_id: str

    topic: str
    difficulty_level: str

    # Text content
    definition: str = ""
    explanation: str = ""
    examples: List[str] = []
    key_points: List[str] = []
    summary: str = ""

    # Extracted visual concepts
    concepts: List[str] = []

    # Media
    images: List[ImageData] = []
    videos: List[VideoData] = []
    audio_base64: Optional[str] = None   # base64-encoded MP3

    created_at: datetime = Field(default_factory=datetime.utcnow)


class ContentHistoryItem(BaseModel):
    id: str
    topic: str
    difficulty_level: str
    created_at: datetime
