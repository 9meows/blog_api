import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from pathlib import Path

from app.schemas import UserCreate, User as UserSchema, TokenResponse
from app.models.users import User as UserModel
from app.core.db_depends import get_session_db
from app.auth import hash_password, verify_password, create_access_token


router  = APIRouter(prefix="/api", tags=["auth"])


BASE_DIR = Path(__file__).resolve().parent.parent.parent
MEDIA_ROOT = BASE_DIR / "media" / "avatars"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2 097 152 байт

async def save_user_avatar(file: UploadFile) -> str:
    """
    Сохраняет изображение пользователя и возвращает относительный URL.
    """
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Only JPG, PNG or WebP images are allowed")

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Image is too large")

    extension = Path(file.filename or "").suffix.lower() or ".jpg"
    file_name = f"{uuid.uuid4()}{extension}"
    file_path = MEDIA_ROOT / file_name
    file_path.write_bytes(content)

    return f"/media/avatars/{file_name}"

@router.post("/register", response_model=UserSchema)
async def create_user(user: UserCreate = Depends(UserCreate.as_form),
                      avatar: UploadFile | None = File(None),
                      db: AsyncSession = Depends(get_session_db)):
    """
    Регистрирует нового пользователя
    """
    existing = await db.scalar(select(UserModel).where(UserModel.username == user.username))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким username уже существует")
    
    existing_email = await db.scalar(select(UserModel).where(UserModel.email == user.email))
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с таким email уже существует")
    
    image_url = await save_user_avatar(avatar) if avatar else None
    db_user = UserModel(username = user.username, email = user.email, 
                   hashed_password = hash_password(user.password), avatar=image_url)
     
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user) 
    return db_user 
    
@router.post("/login", response_model=TokenResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session_db)):
    """
    Аутентифицирует пользователя и возвращает access_token
    """
    user = await db.scalar(select(UserModel).where(form_data.username == UserModel.username, UserModel.is_active == True))
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверное имя пользователя или пароль")
    
    token = create_access_token({"sub":user.username})
    
    return TokenResponse(access_token=token)