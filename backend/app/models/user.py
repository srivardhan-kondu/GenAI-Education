from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserPreferences(BaseModel):
    difficulty_level: str = "beginner"  # beginner | intermediate | advanced
    explanation_style: str = "detailed"  # short | detailed
    visual_learning: bool = True


class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    preferences: Optional[UserPreferences] = None


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    preferences: UserPreferences
    created_at: datetime
