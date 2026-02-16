from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas import UserCreate, User as UserSchema, TokenResponse
from app.models.users import User as UserModel
from app.core.db_depends import get_session_db
from app.auth import hash_password, verify_password, create_access_token


router  = APIRouter(prefix="/api", tags=["auth"])


@router.post("/register", response_model=UserSchema)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_session_db)):
    
    existing = await db.scalar(select(UserModel).where(UserModel.username == user.username))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким username уже существует")
    
    existing_email = await db.scalar(select(UserModel).where(UserModel.email == user.email))
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким email уже существует")

    db_user = UserModel(username = user.username, email = user.email, 
                   hashed_password = hash_password(user.password)) 
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user) 
    return db_user 
    
@router.post("/login", response_model=TokenResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session_db)):
    user = await db.scalar(select(UserModel).where(form_data.username == UserModel.username, UserModel.is_active == True))
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверное имя пользователя или пароль")
    
    token = create_access_token({"sub":user.username})
    
    return TokenResponse(access_token=token)