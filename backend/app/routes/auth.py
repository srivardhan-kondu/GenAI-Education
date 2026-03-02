from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.database.connection import get_database
from app.models.user import UserCreate, UserLogin, UserUpdate
from app.utils.auth_utils import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── Register ──────────────────────────────────────────────────────────────────

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    db = get_database()

    if await db.users.find_one({"email": user_data.email}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    user_doc = {
        "name": user_data.name,
        "email": user_data.email,
        "hashed_password": get_password_hash(user_data.password),
        "preferences": {
            "difficulty_level": "beginner",
            "explanation_style": "detailed",
            "visual_learning": True,
        },
        "created_at": datetime.utcnow(),
    }

    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    token = create_access_token({"sub": user_id})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user_id, "name": user_data.name, "email": user_data.email},
    }


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post("/login")
async def login(credentials: UserLogin):
    db = get_database()
    user = await db.users.find_one({"email": credentials.email})

    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    user_id = str(user["_id"])
    token = create_access_token({"sub": user_id})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user_id, "name": user["name"], "email": user["email"]},
    }


# ── Me ────────────────────────────────────────────────────────────────────────

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "name": current_user["name"],
        "email": current_user["email"],
        "preferences": current_user.get("preferences", {}),
        "created_at": current_user.get("created_at"),
    }


# ── Update Profile ────────────────────────────────────────────────────────────

@router.put("/profile")
async def update_profile(
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user),
):
    db = get_database()
    patch: dict = {}

    if update_data.name:
        patch["name"] = update_data.name
    if update_data.preferences:
        patch["preferences"] = update_data.preferences.model_dump()

    if patch:
        await db.users.update_one(
            {"_id": ObjectId(current_user["id"])}, {"$set": patch}
        )

    updated = await db.users.find_one({"_id": ObjectId(current_user["id"])})
    return {
        "id": str(updated["_id"]),
        "name": updated["name"],
        "email": updated["email"],
        "preferences": updated.get("preferences", {}),
    }
