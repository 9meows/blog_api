from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker


async def get_session_db():
    async with async_session_maker() as session:
        yield session
        

        
