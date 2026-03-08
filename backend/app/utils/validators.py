import re

from fastapi import HTTPException

VALID_DIFFICULTY_LEVELS = {"beginner", "intermediate", "advanced"}
VALID_EXPLANATION_STYLES = {"short", "detailed"}

# Block characters that have no place in a topic string
_INVALID_CHARS = re.compile(r"[<>{}|\\^`]")


def validate_topic(topic: str) -> str:
    topic = topic.strip()
    if len(topic) < 2:
        raise HTTPException(status_code=400, detail="Topic must be at least 2 characters.")
    if len(topic) > 200:
        raise HTTPException(status_code=400, detail="Topic must be at most 200 characters.")
    if _INVALID_CHARS.search(topic):
        raise HTTPException(status_code=400, detail="Topic contains invalid characters.")
    return topic


def validate_difficulty(level: str) -> str:
    level = level.lower().strip()
    if level not in VALID_DIFFICULTY_LEVELS:
        raise HTTPException(
            status_code=400,
            detail=f"difficulty_level must be one of: {', '.join(VALID_DIFFICULTY_LEVELS)}",
        )
    return level


def validate_style(style: str) -> str:
    style = style.lower().strip()
    if style not in VALID_EXPLANATION_STYLES:
        raise HTTPException(
            status_code=400,
            detail=f"explanation_style must be one of: {', '.join(VALID_EXPLANATION_STYLES)}",
        )
    return style
