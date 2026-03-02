import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

logger = logging.getLogger(__name__)


class _Database:
    client: AsyncIOMotorClient = None


_db = _Database()


async def connect_to_mongo() -> None:
    logger.info("Connecting to MongoDB…")
    _db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    # Ensure indexes exist
    db = _db.client[settings.DATABASE_NAME]
    await db.users.create_index("email", unique=True)
    await db.learning_modules.create_index("user_id")
    await db.learning_modules.create_index("topic")
    logger.info("MongoDB connected.")


async def close_mongo_connection() -> None:
    if _db.client:
        _db.client.close()
        logger.info("MongoDB connection closed.")


def get_database():
    return _db.client[settings.DATABASE_NAME]
