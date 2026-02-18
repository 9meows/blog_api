from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.db_depends import get_session_db
from app.models.posts import Post as PostModel
from app.models.comments import Comment as CommentModel
from app.models.tags import Tag, post_tags

router = APIRouter(prefix="/api", tags=["stats"])


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_session_db)):
    """
    Возврщает статистику:
        общее количество статей
        общее количество комментариев;
        самые популярные теги.
    """
    all_posts = await db.scalar(select(func.count(PostModel.id)).where(PostModel.status == "published"))
    
    all_comments = await db.scalar(select(func.count(CommentModel.id)))
    
    populars_tags = await db.execute(select(Tag.name, Tag.slug, func.count(post_tags.c.post_id)
                                            .label("count"))
                                     .join(post_tags, Tag.id == post_tags.c.tag_id)
                                     .join(PostModel, PostModel.id == post_tags.c.post_id)
                                     .where(PostModel.status == "published").group_by(Tag.id)
                                     .order_by(func.count(post_tags.c.post_id).desc()).limit(10))
    
    return {"total_posts": all_posts, "total_comments": all_comments, 
            "popular_tags":[{"name":row.name, "slug":row.slug, "count":row.count} for row in populars_tags]}



@router.get("/tags/cloud/")
async def get_tag_cload(db: AsyncSession = Depends(get_session_db)):
    """
    Возвращает все теги "published" статей
    """
    tags = await db.execute(select(Tag.name, Tag.slug, func.count(post_tags.c.post_id).label("count"))
                            .join(post_tags, Tag.id == post_tags.c.tag_id).join(PostModel, PostModel.id == post_tags.c.post_id)
                            .where(PostModel.status == "published")
                            .group_by(Tag.id)
                            .order_by(func.count(post_tags.c.post_id).desc()))
    
    return {"tags":[{"name":row.name, "slug":row.slug, "count":row.count} for row in tags]}

