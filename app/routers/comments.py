import html
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.users import User as UserModel
from app.models.posts import Post as PostModel
from app.models.comments import Comment as CommentModel
from app.core.db_depends import get_session_db
from app.schemas import CommentCreate, Comment
from app.auth import get_current_user

router = APIRouter(prefix="/api", tags=["comments"])


@router.get("/posts/{slug}/comments", response_model=list[Comment])
async def get_comments_by_slug(
    slug: str,  
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_session_db)
):
    post = await db.scalar(
        select(PostModel).where(PostModel.slug == slug, PostModel.status == "published")
    )
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден")

    comments = await db.scalars(
        select(CommentModel)
        .where(CommentModel.post_id == post.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return comments.all()


@router.post("/posts/{slug}/comments", status_code=status.HTTP_201_CREATED)
async def create_comment(
    slug: str,
    comment: CommentCreate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_session_db)
):
    post = await db.scalar(
        select(PostModel).where(PostModel.slug == slug, PostModel.status == "published")
    )
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден")

    if comment.parent_id is not None:
        parent = await db.scalar(
            select(CommentModel).where(
                CommentModel.id == comment.parent_id,
                CommentModel.post_id == post.id
            )
        )
        if parent is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Родительский комментарий не найден")
    safe_text = html.escape(comment.text)

    db_comment = CommentModel(
        post_id=post.id,
        author_id=current_user.id,
        text=safe_text,
        parent_id=comment.parent_id
    )
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment


@router.delete("/comments/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    id: int,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_session_db)
):
    comment = await db.scalar(
        select(CommentModel).where(CommentModel.id == id)
    )
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Комментарий не найден")

    post = await db.scalar(
        select(PostModel).where(PostModel.id == comment.post_id)
    )

    is_comment_author = comment.author_id == current_user.id
    is_post_author = post.author_id == current_user.id

    if not (is_comment_author or is_post_author):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав для удалеаия")

    await db.delete(comment)
    await db.commit()