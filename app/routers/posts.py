from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from slugify import slugify
from sqlalchemy.orm import selectinload
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache

from app.models.users import User as UserModel  
from app.models.posts import Post as PostModel
from app.models.tags import Tag
from app.core.db_depends import get_session_db
from app.schemas import Post, PostCreate, PostUpdate, PostShort
from app.auth import get_current_user

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.get("/", response_model=list[PostShort])
@cache(expire=300)
async def get_all_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    tag: str | None = Query(None),
    author: str | None = Query(None),
    db: AsyncSession = Depends(get_session_db)
):
    stmt = select(PostModel).where(PostModel.status == "published")

    if author:
        user = await db.scalar(select(UserModel).where(UserModel.username == author))
        if user is None:
            return []
        stmt = stmt.where(PostModel.author_id == user.id)

    if tag:
        tag_obj = await db.scalar(select(Tag).where(Tag.slug == tag))
        if tag_obj is None:
            return []
        stmt = stmt.where(PostModel.tags.any(Tag.id == tag_obj.id))

    posts = await db.scalars(stmt.options(selectinload(PostModel.tags), selectinload(PostModel.author)).offset((page - 1) * page_size).limit(page_size))
    
    reslt = [PostShort(
            id=post.id,
            title=post.title,
            slug=post.slug,
            author=post.author,
            created_at=post.created_at,
            status=post.status,
            view_count=post.view_count,
            tags=post.tags,
            preview=post.content[:200]
        )
        for post in posts.all()
    ]
    return reslt
    


@router.get("/{slug}", response_model=Post)
async def get_post_by_slug(slug: str, db: AsyncSession = Depends(get_session_db)):
    post = await db.scalar(
        select(PostModel).where(PostModel.slug == slug, PostModel.status == "published")
    )
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Статья не найдена")

    await db.execute(
        update(PostModel).where(PostModel.id == post.id).values(view_count=PostModel.view_count + 1)
    )
    await db.commit()
    post = await db.scalar(select(PostModel).options(selectinload(PostModel.tags), selectinload(PostModel.author)).where(PostModel.slug == slug, PostModel.status == "published"))
    return post


@router.post("/", response_model=Post, status_code=status.HTTP_201_CREATED) 
async def create_post(
    post: PostCreate,
    current_user: UserModel = Depends(get_current_user), 
    db: AsyncSession = Depends(get_session_db)
):
    base_slug = slugify(post.title)
    slug_post = base_slug
    counter = 1
    while await db.scalar(select(PostModel).where(PostModel.slug == slug_post)):
        slug_post = f"{base_slug}-{counter}"
        counter += 1

    tags = []
    for tag_name in post.tags:
        tag = await db.scalar(select(Tag).where(Tag.name == tag_name))
        if tag is None:
            tag = Tag(name=tag_name, slug=slugify(tag_name))
            db.add(tag)
            await db.flush()
        tags.append(tag)

    db_post = PostModel(
        title=post.title,
        slug=slug_post,
        content=post.content,
        status=post.status,
        author_id=current_user.id,
        tags=tags
    )
    db.add(db_post)
    await db.commit()
    await FastAPICache.clear(namespace="blog-cache")
    post = await db.scalar(select(PostModel).options(selectinload(PostModel.tags), selectinload(PostModel.author)).where(PostModel.id == db_post.id))

    return post


@router.put("/{slug}", response_model=Post)
async def update_post(
    slug: str,
    post_data: PostUpdate,                                
    current_user: UserModel = Depends(get_current_user), 
    db: AsyncSession = Depends(get_session_db)
):
    post = await db.scalar(select(PostModel).options(selectinload(PostModel.tags), selectinload(PostModel.author)).where(PostModel.slug == slug))
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав для редактирования")

    if post_data.title is not None:
        post.title = post_data.title
    if post_data.content is not None:
        post.content = post_data.content
    if post_data.status is not None:
        post.status = post_data.status

    if post_data.tags is not None:
        tags = []
        for tag_name in post_data.tags:
            tag = await db.scalar(select(Tag).where(Tag.name == tag_name))
            if tag is None:
                tag = Tag(name=tag_name, slug=slugify(tag_name))
                db.add(tag)
                await db.flush()
            tags.append(tag)
        post.tags = tags

    await db.commit()
    await db.refresh(post)
    await FastAPICache.clear(namespace="blog-cache")

    return post


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_by_slug(
    slug: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_session_db)
):
    post = await db.scalar(select(PostModel).where(PostModel.slug == slug))
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пост не найден")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет прав для удаления")

    await db.delete(post)
    await db.commit()
    await FastAPICache.clear(namespace="blog-cache")
    

