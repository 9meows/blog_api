import time
from typing import Dict
from fastapi import FastAPI, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from pydantic import BaseModel
from redis import asyncio as aioredis
from contextlib import asynccontextmanager
from fastapi_cache.decorator import cache
from starlette.requests import Request
from fastapi.staticfiles import StaticFiles


from app.routers import auth, users, posts, comments, stats, search, sentiment

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url("redis://redis:6379/0")
    
    try:
        await redis.ping()
        FastAPICache.init(RedisBackend(redis), prefix="blog-cache")
        yield
    except Exception as e:
        print(f"Ошьбка подключения к редису:(: {e}")
    finally:
        await redis.close()

app = FastAPI(title="Blog API", lifespan=lifespan)

app.mount("/media", StaticFiles(directory="media"), name="media")    
    
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(stats.router)
app.include_router(search.router)
app.include_router(sentiment.router)

@app.get("/hp")
async def get_health() -> dict:
    return {"message": "ok"}

