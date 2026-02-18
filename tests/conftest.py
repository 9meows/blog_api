import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from app.main import app
from app.core.database import Base
from app.core.db_depends import get_session_db

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@test_db:5432/test_blog_db"

test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
test_session_maker = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) 
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with test_session_maker() as session:
        yield session
        await session.execute(
            text("TRUNCATE TABLE comments, post_tags, posts, users, tags RESTART IDENTITY CASCADE")
        )
        await session.commit()


@pytest_asyncio.fixture
async def client(db_session):
    async def override_db():
        yield db_session

    app.dependency_overrides[get_session_db] = override_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        FastAPICache.init(InMemoryBackend(), prefix="test")
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(client):
    await client.post("/api/register", data={
        "username": "testuser",
        "email": "test@example.com",
        "password": "qwerty"
    })
    response = await client.post("/api/login", data={
        "username": "testuser",
        "password": "qwerty"
    })
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client