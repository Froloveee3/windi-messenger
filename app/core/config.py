from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict


class Settings(BaseSettings):
    SECRET_KEY: str = "I0KjnLaDg8WnK-xY1ynHh1xn-uNPActP32hmi8Z7OT8"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    DATABASE_URL: str
    
    SCOPES: Dict[str, str] = {
        "me": "Read information about the current user",
        "users:read": "Read all users (admin only)",
        "users:write": "Manage users (admin only)",
        "chats:read": "Read chats list and details",
        "chats:write": "Create new chats",
        "messages:read": "Read chat history",
        "messages:write": "Send messages",
    }
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()
