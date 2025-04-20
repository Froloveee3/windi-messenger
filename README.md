# WinDI Messenger

Мини‑мессенджер с текстовым чатом и групповыми комнатами на FastAPI + WebSocket, по мотивам Telegram.

## 🚀 Стек
- **Python 3.12**, FastAPI, asyncio  
- **SQLAlchemy** (асинхронный ORM) + PostgreSQL  
- **WebSocket** для real‑time обмена  
- **Docker & Docker Compose** для контейнеризации  
- **Alembic** для миграций  
- **Pytest** для тестов  

## 📋 Функционал
1. **WebSocket чат**  
   - Личные и групповые чаты  
   - Сохранение сообщений в БД  
   - Статус «прочитано»  
   - Уникальный `client_msg_id` для дедупликации  
2. **REST API**  
   - JWT‑авторизация (`/api/v1/auth/token`)  
   - CRUD для пользователей и чатов  
   - История сообщений:  
     ```http
     GET /api/v1/history/{chat_id}?skip=0&limit=100
     ```
3. **Тесты** — 19 пройденных тестов Pytest (пример запуска ниже).

## 🛠 Быстрый старт

1. **Клонируем репозиторий:**
    ```bash
    git clone https://github.com/Froloveee3/windi-messenger.git
    cd windi-messenger
    ```
2. **Создаём `.env`:**
    - Копируем `.env.example` в `.env`:
        ```bash
        cp .env.example .env
        ```
    - В `.env` задать переменные (пример):
        ```dotenv
        POSTGRES_USER=postgres
        POSTGRES_PASSWORD=postgres
        POSTGRES_DB=messenger
        POSTGRES_TEST_DB=messenger_test
        POSTGRES_PORT=5432
        
        DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:${POSTGRES_PORT}/${POSTGRES_DB}
        
        SECRET_KEY=I0KjnLaDg8WnK-xY1ynHh1xn-uNPActP32hmi8Z7OT8
        ```
3. **Собираем и запускаем всё через Docker Compose:**
    ```bash
    docker compose up --build
    ```
4. **Бэкенд доступен на** http://localhost:8000/:  
    - **Healthcheck:** GET /api/v1/health/  
    - **Swagger/OpenAPI:** http://localhost:8000/docs  
    - **ReDoc:** http://localhost:8000/redoc
5. **Запуск тестов (контейнер “test”):**
    ```bash
    docker compose run --rm test
    # 19 passed, 3 warnings
    ```

## 📖 Примеры API
1. **Получить токен**
    ```bash
    curl -X POST http://localhost:8000/api/v1/auth/token \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=user@example.com&password=secret"
    ```
2. **Создать пользователя**
    ```bash
    curl -X POST http://localhost:8000/api/v1/users/ \
        -H "Authorization: Bearer <TOKEN>" \
        -H "Content-Type: application/json" \
        -d '{"name":"User","email":"user@test.com","password":"secret"}'
    ```
3. **WebSocket соединение**
    - Подключение к Websocket:
        ```bash
        wscat -c "ws://localhost:8000/api/v1/ws/<CHAT_ID>?token=<TOKEN>"
        ```
    - Отправка сообщения:
        ```bash
        {"type": "message", "text": "Some text", "client_msg_id": "msg-1"}
        ```
    - Прочтение сообщения:
        ```bash
        {"type":"read","message_id":<MESSAGE_ID>}
        ```

## 📂 Миграции
- Скрипты в `alembic/versions/` находятся в репозитории.
- При старте контейнера выполняется:
    ```bash
    alembic upgrade head
    ```

## 🛡 Права администратора
По умолчанию все новые пользователи создаются с `is_admin = FALSE`. Чтобы дать пользователю права администратора:
```bash
# Например, если POSTGRES_USER=postgres и POSTGRES_DB=messenger
docker compose exec db psql -U postgres -d messenger
```

После входа в консоль выполните SQL:

```sql
UPDATE users
SET is_admin = TRUE
WHERE id = 1;
```

Проверка:
```sql
SELECT id, name, email, is_admin
FROM users
WHERE id = 1;
```

Пользователь с `id = 1` теперь обладает административными командами.

## ✅ Тестирование
```bash
# Запуск тестов
docker compose run --rm test
# Вывод: 19 passed, 3 warnings
```