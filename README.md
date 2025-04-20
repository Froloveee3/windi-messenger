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
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/messenger
   ```
3. **Собираем и запускаем всё через Docker Compose:**
    ```bash
    docker compose up --build
    ```
4. **Бэкенд доступен на http://localhost:8000/:**
    - **Healthcheck:** GET /api/v1/health/
    - **Swagger/OpenAPI:** http://localhost:8000/docs
    - **ReDoc:** http://localhost:8000/redoc
5. **Чтобы миграции применились автоматически, в Dockerfile прописано:**
    ```bash
    alembic upgrade head
    ```
6. **Запуск тестов (контейнер “test”):**
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
## ✅ Тестирование
```bash
docker compose run --rm test
# Вывод: 19 passed, 3 warnings
```

## 📂 Миграции
- Скрипты в alembic/versions/
- При старте контейнера:
    ```bash
    alembic upgrade head
    ```





