from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.core.db_depends import get_session_db
from app.models.posts import Post as PostModel
from app.schemas import PostShort

router = APIRouter(prefix="/api", tags=["search"])

@router.get("/search")
async def search_post(q: str | None = Query(None, description="Поиск по заголовку и содержанию"),
                      page: int = Query(1, ge=1),
                      page_size: int = Query(10, ge=1, le=100),
                      db: AsyncSession = Depends(get_session_db)):
    """
    LIKE-поиск по заголовку и содержанию.
    Возвращает список постов
    """
    filters = [PostModel.status == "published"]
    if q is not None:
        search_value = q.strip()
        if search_value:
            filters.append(
                or_(func.lower(PostModel.title).like(f"%{search_value.lower()}%"),
                    func.lower(PostModel.content).like(f"%{search_value.lower()}%")))                           
                                    
    posts = await db.scalars(select(PostModel).options(selectinload(PostModel.author), selectinload(PostModel.tags)).
                             where(*filters).offset((page - 1) * page_size).limit(page_size))
    
    return [PostShort(id=post.id,
                      title=post.title,
                      slug=post.slug,
                      author=post.author,
                      created_at=post.created_at,
                      status=post.status,
                      view_count=post.view_count
                      ,tags=post.tags,
                      preview=post.content[:200])
            for post in posts.all()
            ]