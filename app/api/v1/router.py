from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.chats import router as chats_router, history_router
from app.api.v1.endpoints.ws import router as ws_router


api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(chats_router, prefix="/chats", tags=["chats"])
api_router.include_router(history_router, prefix="/history", tags=["history"])
api_router.include_router(ws_router, prefix="/ws", tags=["ws"])
