from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.settings import get_settings
from src.utils.logger import logger

settings = get_settings()

# Configure Async PostgreSQL Engine
# Using pool_pre_ping to automatically discard dead connections
engine_args = {
    "echo": False,
    "pool_pre_ping": True,
}

if "postgresql" in settings.DATABASE_URL:
    engine_args["pool_size"] = settings.DB_POOL_SIZE
    engine_args["max_overflow"] = settings.DB_MAX_OVERFLOW

engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, **engine_args)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def transaction_scope() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for explicit transaction control."""
    async with async_session_factory() as session:
        async with session.begin():
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.error(f"Transaction rolled back due to error: {e}")
                raise
