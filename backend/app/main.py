import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="google")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.connection import connect_to_mongo, close_mongo_connection
from app.routes import auth, content, notes, search

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered platform that auto-generates multimodal educational content from any topic.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Lifecycle ─────────────────────────────────────────────────────────────────
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(content.router)
app.include_router(notes.router)
app.include_router(search.router)


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}
