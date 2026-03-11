import asyncio
import base64
import io
import logging
import platform
import tempfile
from typing import List, Optional

import httpx
import numpy as np
from moviepy import ImageClip, CompositeVideoClip, TextClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

from app.config import settings

logger = logging.getLogger(__name__)

_OPENAI_IMG_URL = "https://api.openai.com/v1/images/generations"

# Video settings
_CLIP_DURATION = 5       # seconds per concept slide
_FPS = 24
_VIDEO_SIZE = (640, 360)  # smaller resolution to keep MongoDB doc under 16 MB


def _get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a TrueType font cross-platform, falling back to Pillow default."""
    candidates = []
    system = platform.system()
    if system == "Darwin":  # macOS
        candidates = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFNSText.ttf",
        ]
    elif system == "Windows":
        candidates = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
        ]
    else:  # Linux
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
        ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


class VideoGenerationService:
    """
    Generates animated educational MP4 videos by:
      1. Creating concept images via OpenAI DALL-E
      2. Building an MP4 slideshow with zoom/pan effects and text overlays
         using moviepy (local)
    """

    def __init__(self) -> None:
        self.api_key = settings.OPENAI_API_KEY

    async def _generate_concept_image(self, concept: str, topic: str) -> Optional[bytes]:
        """Fetch a concept image from OpenAI DALL-E and return raw bytes."""
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set — skipping video image generation.")
            return None

        prompt = (
            f"Educational diagram illustrating '{concept}' as part of {topic}. "
            "Clean infographic, labeled sections, arrows, white background, "
            "professional educational style, suitable for students, high quality."
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
                resp = await client.post(_OPENAI_IMG_URL, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return base64.b64decode(data["data"][0]["b64_json"])

                # Fall back to DALL-E 2 if DALL-E 3 fails
                logger.warning("DALL-E 3 failed [%s] for video, trying DALL-E 2...", resp.status_code)
                payload["model"] = "dall-e-2"
                payload["size"] = "512x512"
                resp = await client.post(_OPENAI_IMG_URL, headers=headers, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return base64.b64decode(data["data"][0]["b64_json"])

                logger.error("Image fetch failed [%s]: %s", resp.status_code, resp.text[:300])
        except Exception:
            logger.exception("Image fetch error for concept '%s'", concept)
        return None

    def _create_title_frame(self, topic: str) -> np.ndarray:
        """Create a title/intro frame as a numpy array."""
        img = Image.new("RGB", _VIDEO_SIZE, color=(30, 30, 60))
        draw = ImageDraw.Draw(img)

        # Title text
        title = f"Learn: {topic}"
        if len(title) > 40:
            title = title[:37] + "..."

        font_large = _get_font(52)
        font_small = _get_font(28)

        # Center title
        bbox = draw.textbbox((0, 0), title, font=font_large)
        tw = bbox[2] - bbox[0]
        draw.text(
            ((_VIDEO_SIZE[0] - tw) // 2, _VIDEO_SIZE[1] // 2 - 60),
            title, fill="white", font=font_large,
        )

        # Subtitle
        subtitle = "AI-Generated Educational Video"
        bbox2 = draw.textbbox((0, 0), subtitle, font=font_small)
        sw = bbox2[2] - bbox2[0]
        draw.text(
            ((_VIDEO_SIZE[0] - sw) // 2, _VIDEO_SIZE[1] // 2 + 20),
            subtitle, fill=(150, 180, 255), font=font_small,
        )

        return np.array(img)

    def _create_concept_frame(self, concept: str, image_bytes: Optional[bytes]) -> np.ndarray:
        """Compose a concept frame: image + label bar at the bottom."""
        canvas = Image.new("RGB", _VIDEO_SIZE, color=(245, 245, 250))

        if image_bytes:
            try:
                concept_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
                # Fit image into the upper portion
                img_area = (_VIDEO_SIZE[0] - 40, _VIDEO_SIZE[1] - 120)
                concept_img.thumbnail(img_area, Image.LANCZOS)
                x = (_VIDEO_SIZE[0] - concept_img.width) // 2
                y = (img_area[1] - concept_img.height) // 2 + 10
                canvas.paste(concept_img, (x, y))
            except Exception:
                pass

        # Label bar at bottom
        draw = ImageDraw.Draw(canvas)
        draw.rectangle(
            [(0, _VIDEO_SIZE[1] - 80), (_VIDEO_SIZE[0], _VIDEO_SIZE[1])],
            fill=(30, 30, 60),
        )
        font = _get_font(30)

        label = f"Concept: {concept}"
        bbox = draw.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(
            ((_VIDEO_SIZE[0] - tw) // 2, _VIDEO_SIZE[1] - 60),
            label, fill="white", font=font,
        )

        return np.array(canvas)

    def _build_video(
        self, topic: str, concept_frames: List[tuple[str, np.ndarray]]
    ) -> Optional[str]:
        """Build an MP4 from concept frames with zoom effect. Returns base64 MP4."""
        clips = []

        # Title slide
        title_arr = self._create_title_frame(topic)
        title_clip = ImageClip(title_arr, duration=3)
        clips.append(title_clip)

        # Concept slides with slow zoom
        for _concept, frame_arr in concept_frames:
            base_clip = ImageClip(frame_arr, duration=_CLIP_DURATION)

            # Slow zoom: scale from 1.0 to 1.08 over the clip duration
            def make_zoom(clip):
                def zoom_effect(get_frame, t):
                    scale = 1.0 + 0.08 * (t / clip.duration)
                    frame = get_frame(t)
                    h, w = frame.shape[:2]
                    new_h, new_w = int(h * scale), int(w * scale)
                    from PIL import Image as PILImage
                    img = PILImage.fromarray(frame).resize((new_w, new_h), PILImage.LANCZOS)
                    arr = np.array(img)
                    # Crop back to original size from center
                    cy, cx = new_h // 2, new_w // 2
                    return arr[cy - h // 2: cy - h // 2 + h, cx - w // 2: cx - w // 2 + w]
                return clip.transform(zoom_effect)

            zoomed = make_zoom(base_clip)
            clips.append(zoomed)

        # Concatenate all clips
        final = concatenate_videoclips(clips, method="compose")

        # Write to temp file and read back as base64
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=True) as tmp:
                final.write_videofile(
                    tmp.name,
                    fps=_FPS,
                    codec="libx264",
                    audio=False,
                    logger=None,
                    preset="ultrafast",
                    ffmpeg_params=["-crf", "32"],
                )
                final.close()
                tmp.seek(0)
                return base64.b64encode(tmp.read()).decode("utf-8")
        except Exception:
            logger.exception("Video encoding failed")
            final.close()
            return None

    async def generate_video(self, concept: str, topic: str) -> Optional[str]:
        """Generate a single-concept animated video. Returns base64 MP4."""
        img_bytes = await self._generate_concept_image(concept, topic)
        frame = self._create_concept_frame(concept, img_bytes)

        # Build video in a thread to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._build_video, topic, [(concept, frame)]
        )

    async def generate_videos_for_concepts(
        self, concepts: List[str], topic: str
    ) -> List[dict]:
        """Generate one combined animated video from up to 3 concepts."""
        subset = concepts[:3]

        # Fetch all concept images concurrently
        img_tasks = [self._generate_concept_image(c, topic) for c in subset]
        img_results = await asyncio.gather(*img_tasks, return_exceptions=True)

        # Build frames
        concept_frames = []
        for concept, img_result in zip(subset, img_results):
            img_bytes = img_result if isinstance(img_result, bytes) else None
            frame = self._create_concept_frame(concept, img_bytes)
            concept_frames.append((concept, frame))

        # Build one combined video in a thread
        loop = asyncio.get_event_loop()
        b64 = await loop.run_in_executor(
            None, self._build_video, topic, concept_frames
        )

        # Return as a single video entry with the topic as concept
        return [{"concept": f"{topic} — Overview", "base64_data": b64}]


video_generation_service = VideoGenerationService()
