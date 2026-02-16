from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.users import User as UserModel
from app.models.posts import Post as PostModel
from app.core.db_depends import get_session_db
from app.schemas import User

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/", response_model=list[User])
async def get_all_users(page: int = Query(1, ge=1),
                        page_size: int = Query(10, ge=1, le=100),
                        db: AsyncSession = Depends(get_session_db)):
    all_users = await db.scalars(select(UserModel).where(UserModel.is_active == True).offset((page - 1) * page_size).limit(page_size))
    return all_users.all()


@router.get("/{username}/posts")
async def get_user_posts_by_username(username: str, 
                                     page: int = Query(1, ge=1),
                                     page_size: int = Query(10, ge=1, le=100),
                                     db: AsyncSession = Depends(get_session_db)):
    
    user = await db.scalar(select(UserModel).where(UserModel.username == username, UserModel.is_active == True))
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    posts_user = await db.scalars(select(PostModel).where(user.id == PostModel.author_id, PostModel.status == "published")
                                    .offset((page - 1) * page_size).limit(page_size))
    
    
    return posts_user.all()

@router.get("/{username}", response_model=User)
async def get_user_by_username(username: str, db: AsyncSession = Depends(get_session_db)):
    user = await db.scalar(select(UserModel).where(UserModel.username == username, UserModel.is_active == True))
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    
    return user
