import asyncio
import base64
import io
import logging
import platform
import tempfile
from typing import List, Optional

import os
import numpy as np
from moviepy import ImageClip, CompositeVideoClip, TextClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

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
    Generates animated educational MP4 videos by building a slideshow
    from pre-generated images with zoom/pan effects and text overlays
    using moviepy.
    """

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
        tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        tmp_path = tmp.name
        tmp.close()
        try:
            final.write_videofile(
                tmp_path,
                fps=_FPS,
                codec="libx264",
                audio=False,
                logger=None,
                preset="ultrafast",
                ffmpeg_params=["-crf", "32"],
            )
            final.close()
            with open(tmp_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            logger.exception("Video encoding failed")
            final.close()
            return None
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    async def generate_video(self, concept: str, topic: str, image_b64: Optional[str] = None) -> Optional[str]:
        """Generate a single-concept animated video from a pre-generated image. Returns base64 MP4."""
        img_bytes = base64.b64decode(image_b64) if image_b64 else None
        frame = self._create_concept_frame(concept, img_bytes)

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._build_video, topic, [(concept, frame)]
        )

    async def generate_videos_for_concepts(
        self, concepts: List[str], topic: str, images: List[dict] = None
    ) -> List[dict]:
        """Generate one combined animated slideshow video from pre-generated images."""
        subset = concepts[:3]
        image_map = {
            img["concept"]: img.get("base64_data")
            for img in (images or [])
            if img.get("base64_data")
        }

        concept_frames = []
        for concept in subset:
            b64_data = image_map.get(concept)
            img_bytes = base64.b64decode(b64_data) if b64_data else None
            frame = self._create_concept_frame(concept, img_bytes)
            concept_frames.append((concept, frame))

        loop = asyncio.get_event_loop()
        b64 = await loop.run_in_executor(
            None, self._build_video, topic, concept_frames
        )

        return [{"concept": f"{topic} — Overview", "base64_data": b64}]


video_generation_service = VideoGenerationService()
