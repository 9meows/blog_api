# Blog API

REST API блог-платформы с пользователями, статьями, комментариями и тегами. Реализованы все требования основного задания и дополнительные функции: кеширование, поиск, статистика, облако тегов, загрузка аватаров.

## Стек технологий

- Python 3.11
- FastAPI
- SQLAlchemy (ORM) + Alembic
- PostgreSQL
- Pydantic
- Pytest
- Docker + Docker Compose

---

# Быстрый старт через Docker

### 1. Клонировать репозиторий

```bash
git clone 
cd blog_api
```

### 2. Создать файл `.env`

```bash
cp .env.example .env
```

Содержимое `.env`:

```env
DB_HOST=postgres
DB_PORT=5432
DB_NAME=blog_db
DB_USER=postgres
DB_PASSWORD=postgres

SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Собрать и запустить контейнеры

```bash
docker-compose up -d --build
```

Это запустит:
- PostgreSQL (основная БД)
- PostgreSQL (тестовая БД)
- Redis (кеширование)
- FastAPI приложение

### 4. Применить миграции

```bash
docker-compose exec api alembic upgrade head
```

Приложение доступно:
- API: `http://localhost:8000`
- Интерактивная документация Swagger: `http://localhost:8000/docs`

---

## Запуск тестов

```bash
docker-compose exec api bash -c "cd /app && pytest tests/ -v"
```

Покрытие тестами: 16 тестов на основные эндпоинты (auth, posts, comments, users).

---

## API Endpoints

### Аутентификация

#### Регистрация пользователя

```bash
curl -X POST http://localhost:8000/api/register \
  -F "username=john" \
  -F "email=john@example.com" \
  -F "password=secret123"
```

С загрузкой аватара:

```bash
curl -X POST http://localhost:8000/api/register \
  -F "username=john" \
  -F "email=john@example.com" \
  -F "password=secret123" \
  -F "avatar=@/path/to/avatar.jpg"
```

#### Вход (получение токена)

```bash
curl -X POST http://localhost:8000/api/login \
  -F "username=john" \
  -F "password=secret123"
```

Ответ:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### Статьи

#### Список статей (с кешированием)

```bash
# все статьи
curl http://localhost:8000/api/posts/

# с фильтрацией по тегу
curl http://localhost:8000/api/posts/?tag=python

# с фильтрацией по автору
curl http://localhost:8000/api/posts/?author=john

# с пагинацией
curl "http://localhost:8000/api/posts/?page=2&page_size=5"
```

Список статей кешируется в Redis на 5 минут.

#### Получение статьи по slug

```bash
curl http://localhost:8000/api/posts/moi-pervyi-post/
```

Возвращает полную статью со всеми комментариями. При каждом запросе увеличивается счётчик просмотров.

#### Создание статьи

```bash
curl -X POST http://localhost:8000/api/posts/ \
  -H "Authorization: Bearer " \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Заголовок статьи",
    "content": "Текст статьи не менее 100 символов. Здесь может быть любой контент включая markdown разметку для изображений.",
    "status": "published",
    "tags": ["python", "fastapi"]
  }'
```

Теги создаются автоматически если их нет в базе.

#### Обновление статьи

```bash
curl -X PUT http://localhost:8000/api/posts/moi-pervyi-post/ \
  -H "Authorization: Bearer " \
  -H "Content-Type: application/json" \
  -d '{"title": "Новый заголовок", "status": "draft"}'
```

Только автор статьи может её редактировать.

#### Удаление статьи

```bash
curl -X DELETE http://localhost:8000/api/posts/moi-pervyi-post/ \
  -H "Authorization: Bearer "
```

Только автор статьи может её удалить.

---

### Комментарии

#### Комментарии к статье

```bash
curl http://localhost:8000/api/posts/moi-pervyi-post/comments

# с пагинацией
curl "http://localhost:8000/api/posts/moi-pervyi-post/comments?page=1&page_size=10"
```

#### Добавление комментария

```bash
curl -X POST http://localhost:8000/api/posts/moi-pervyi-post/comments \
  -H "Authorization: Bearer " \
  -H "Content-Type: application/json" \
  -d '{"text": "Отличная статья!"}'
```

#### Ответ на комментарий

```bash
curl -X POST http://localhost:8000/api/posts/moi-pervyi-post/comments \
  -H "Authorization: Bearer " \
  -H "Content-Type: application/json" \
  -d '{"text": "Спасибо за комментарий!", "parent_id": 1}'
```

#### Удаление комментария

```bash
curl -X DELETE http://localhost:8000/api/comments/1 \
  -H "Authorization: Bearer "
```

Удалить комментарий может автор комментария или автор статьи.

---

### Пользователи

#### Список пользователей

```bash
curl http://localhost:8000/api/users/

# с пагинацией
curl "http://localhost:8000/api/users/?page=1&page_size=20"
```

#### Профиль пользователя

```bash
curl http://localhost:8000/api/users/john/
```

Возвращает профиль пользователя включая аватар (если загружен).

#### Статьи пользователя

```bash
curl http://localhost:8000/api/users/john/posts/
```

---

### Поиск

#### Поиск по статьям

```bash
curl "http://localhost:8000/api/search?q=python"

# с пагинацией
curl "http://localhost:8000/api/search?q=fastapi&page=1&page_size=5"
```

Поиск выполняется по заголовку и содержанию статей (LIKE-запрос, регистронезависимый).

---

### Статистика

#### Общая статистика

```bash
curl http://localhost:8000/api/stats
```

Ответ:

```json
{
  "total_posts": 42,
  "total_comments": 156,
  "popular_tags": [
    {"name": "python", "slug": "python", "count": 15},
    {"name": "fastapi", "slug": "fastapi", "count": 12},
    {"name": "docker", "slug": "docker", "count": 8}
  ]
}
```

#### Облако тегов

```bash
curl http://localhost:8000/api/tags/cloud/
```

Возвращает все теги с количеством использований, отсортированные по популярности.

---

## Особенности реализации

### Безопасность

- **Хеширование паролей** — bcrypt
- **JWT токены** — для аутентификации
- **XSS защита** — экранирование HTML в комментариях через `html.escape()`
- **Валидация данных** — Pydantic схемы
- **Права доступа**:
  - Анонимные — только чтение статей
  - Авторизованные — создание статей и комментариев
  - Автор — редактирование и удаление своего контента

### Производительность

- **Кеширование** — список статйей кешируется в Redis на 5 минут
- **Eager loading** — использование `selectinload` для оптимизации запросов
- **Индексы** — на внешние ключи (author_id, post_id)
- **Пагинация** — на всех GET-методах списков

### Валидация

- Уникальность `slug` — автоматическая генерация с инкрементом при дублликатах
- Валидный email при регистрации
- Минимальная длина статьи — 100 символов
- Максимальная длина комментария — 2000 символов
- Допустимые статусы статьи — `draft` или `published`

---

## Структура проекта

```
blog_api/
├── app/
│   ├── core/
│   │   ├── config.py          
│   │   ├── database.py         
│   │   └── db_depends.py       
│   ├── migrations/
│   │   ├── versions/           
│   │   ├── env.py              
│   │   └── script.py.mako      
│   ├── models/                 
│   │   ├── users.py            
│   │   ├── posts.py            
│   │   ├── comments.py         
│   │   └── tags.py             
│   ├── routers/                
│   │   ├── auth.py            
│   │   ├── posts.py            
│   │   ├── comments.py        
│   │   ├── users.py            
│   │   ├── search.py           
│   │   └── stats.py           
│   ├── static/
│   │   └── uploads/            
│   │       └── avatars/       
│   ├── auth.py                 
│   ├── schemas.py              
│   └── main.py                 
├── media/                      
│   └── avatars/                
├── tests/
│   ├── conftest.py             
│   ├── test_auth.py            
│   ├── test_posts.py           
│   ├── test_comments.py        
│   └── test_users.py           
├── .env.example                
├── .gitignore
├── docker-compose.yml          
├── Dockerfile                  
├── alembic.ini                
├── pytest.ini                  
├── requirements.txt            
└── README.md
```

