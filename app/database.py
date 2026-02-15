from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.config import settings


class Base(DeclarativeBasee):
    pass


DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

async_engine = create_async_engine(DATABASE_URL)


async_session_maker = async_sessionmaker(bind=async_engine, expire_on_commit=False)

