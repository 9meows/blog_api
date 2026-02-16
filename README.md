# Blog API

REST API блог-платформы с поддержкой пользователей, статей, комментариев и тегов.

## Стек технологий

- Python 3.11
- FastAPI
- SQLAlchemy (ORM) + Alembic
- PostgreSQL
- Pydantic
- Pytest
- Docker + Docker Compose

---

## Запуск через Docker

### 1. Клонировать репозиторий

```bash
git clone <repository_url>
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

### 4. Применить миграции

```bash
docker-compose exec api alembic upgrade head
```

Приложение доступно по адресу: `http://localhost:8000`

Интерактивная документация: `http://localhost:8000/docs`

---

## Запуск тестов

```bash
docker-compose exec api bash -c "cd /app && pytest tests/ -v"
```

---

## Примеры запросов к API

### Регистрация

```bash
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "john@example.com", "password": "secret123"}'
```

### Вход

```bash
curl -X POST http://localhost:8000/api/login \
  -F "username=john" \
  -F "password=secret123"
```

Ответ:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Создание статьи

```bash
curl -X POST http://localhost:8000/api/posts/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Заголовок статьи",
    "content": "Текст статьи не менее 100 символов...",
    "status": "published",
    "tags": ["python", "fastapi"]
  }'
```

### Список статей

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

### Получение статьи

```bash
curl http://localhost:8000/api/posts/zagolovok-stati/
```

### Обновление статьи

```bash
curl -X PUT http://localhost:8000/api/posts/zagolovok-stati/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Новый заголовок"}'
```

### Удаление статьи

```bash
curl -X DELETE http://localhost:8000/api/posts/zagolovok-stati/ \
  -H "Authorization: Bearer <token>"
```

### Комментарии к статье

```bash
curl http://localhost:8000/api/posts/zagolovok-stati/comments
```

### Добавление комментария

```bash
curl -X POST http://localhost:8000/api/posts/zagolovok-stati/comments \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"text": "Текст комментария"}'
```

### Удаление комментария

```bash
curl -X DELETE http://localhost:8000/api/comments/1 \
  -H "Authorization: Bearer <token>"
```

### Список пользователей

```bash
curl http://localhost:8000/api/users/
```

### Профиль пользователя

```bash
curl http://localhost:8000/api/users/john/
```

### Статьи пользователя

```bash
curl http://localhost:8000/api/users/john/posts/
```

---

## Структура проекта

```
blog_api/
├── app/
│   ├── core/
│   │   ├── config.py         # Настройки приложения
│   │   ├── database.py       # Подключение к бд
│   │   └── db_depends.py     # Dependency injection сессии
│   ├── migrations/
│   │   └── versions/         # Файлы миграций Alembic
│   ├── models/               # SQLAlchemy модели
│   ├── routers/              # Эндпоинты
│   ├── auth.py               # JWT аутентификация
│   ├── schemas.py            # Pydantic схемы
│   └── main.py               # Точка входа
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_posts.py
│   ├── test_comments.py
│   └── test_users.py
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
├── pytest.ini
└── requirements.txt
```
