from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator
from typing import Annotated
from datetime import datetime

#Token
class TokenResponse(BaseModel):
    access_token: Annotated[str, Field(description="Access токен")]
    token_type: Annotated[str, Field(description="Тип токена")] = "bearer"
 
# --- USER ---C
class UserCreate(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=50, description="Имя пользователя")]
    email: Annotated[EmailStr, Field(description="Почта пользователя")]
    password: Annotated[str, Field(min_length=6, description="Пароль пользователя(минимум 6 символов)")]

class UserLogin(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=50, description="Имя пользователя")]
    password: Annotated[str, Field(min_length=6, description="Пароль пользователя(минимум 6 символов)")]

class User(BaseModel):
    id: Annotated[int, Field(description="ID пользователя")]
    username: Annotated[str, Field(description="Имя пользователя")]
    email: Annotated[EmailStr, Field(description="Почта пользователя")]
    date_joined: Annotated[datetime, Field(description="Дата присоединения пользователя")]
    is_active: Annotated[bool, Field(description="Активность пользователя")]
    
    model_config = ConfigDict(from_attributes=True)

# tag

class Tag(BaseModel):
    id: Annotated[int, Field(description="ID тэга")]
    name: Annotated[str, Field(description="Имя тэга")]
    slug: Annotated[str, Field(description="URL тэга")]

    model_config = ConfigDict(from_attributes=True)
    
# --- POST ---C

class PostCreate(BaseModel):
    title: Annotated[str, Field(min_length=3, max_length=100, description="Название поста")]
    content: Annotated[str, Field(min_length=100, description="Текст поста(минимум 100 символов)")]
    status: Annotated[str, Field(default="draft", pattern="^(draft|published)$")]

    tags: Annotated[list[str], Field(default_factory=list, description="Список имён тегов")]

    @field_validator("tags", mode="before")
    @classmethod
    def fillter_null_tags(cls, tags):
        if tags is None:
            return tags
        right_tags = []
        for tag in tags:
            if tag is not None:
                right_tags.append(tag)
        return right_tags    
    
    
class PostUpdate(BaseModel):
    title: Annotated[str | None, Field(min_length=3, max_length=100, description="Название поста")] = None
    content: Annotated[str | None, Field(min_length=100, description="Текст поста(минимум 100 символов)")] = None
    status: Annotated[str | None, Field(default="draft", pattern="^(draft|published)$")] = None

    tags: Annotated[list[str] | None, Field(None, description="Список имён тегов")] = None
    
    

class PostShort(BaseModel):
    id: Annotated[int, Field(description="ID поста")]
    title: Annotated[str, Field(min_length=3, max_length=100, description="Название поста")]
    slug: Annotated[str, Field(description="URL поста")]
    author: Annotated[User, Field(description="Автор поста")]
    created_at: Annotated[datetime, Field(description="Дата создания поста")]
    status: Annotated[str, Field(default="draft", pattern="^(draft|published)$")]
    view_count: Annotated[int, Field(description="Кол-во просмотров")]
    tags: Annotated[list[Tag], Field(default_factory=list, description="Список имён тегов")]
    preview: Annotated[str, Field(max_length=200, description="Первые 200 символов текста")]
    
    model_config = ConfigDict(from_attributes=True)
    
class Post(BaseModel):
    id: Annotated[int, Field(description="ID поста")]
    title: Annotated[str, Field(min_length=3, max_length=100, description="Название поста")]
    slug: Annotated[str, Field(description="URL поста")]
    content: Annotated[str, Field(min_length=100, description="Текст поста(минимум 100 символов)")]
    author: Annotated[User, Field(description="Автор поста")]
    created_at: Annotated[datetime, Field(description="Дата создания поста")]
    updated_at: Annotated[datetime, Field(description="Дата обновления поста")]
    status: Annotated[str, Field(default="draft", pattern="^(draft|published)$")]
    view_count: Annotated[int, Field(description="Кол-во просмотров")]
    tags: Annotated[list[Tag], Field(default_factory=list, description="Список имён тегов")]
    
    model_config = ConfigDict(from_attributes=True)
    

    
# --- comment
class CommentCreate(BaseModel):
    text: Annotated[str, Field(min_length=1, max_length=2000, description="Текст поста")]
    
    parent_id: Annotated[int | None, Field(description="ID комментария родителя")] = None

class Comment(BaseModel):
    id: Annotated[int, Field(description="ID комментария")]
    post_id: Annotated[int, Field(description="ID поста для коммента")]
    author: Annotated[User, Field(description="ID автора коммента")]
    text: Annotated[str, Field(description="Текст поста")]
    created_at: Annotated[datetime, Field(description="Время создания комментария")]
    
    parent_id: Annotated[int | None, Field(description="ID комментария родителя")] = None
    
    model_config = ConfigDict(from_attributes=True)
    
