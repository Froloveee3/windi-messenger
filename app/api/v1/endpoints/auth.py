from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models import User
from app.core.config import settings
from app.core.security import verify_password


router = APIRouter(tags=["auth"])


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(select(User).where(User.email == form_data.username))
    user = res.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    scopes = ["me", "chats:read", "chats:write", "messages:read", "messages:write"]
    if getattr(user, "is_admin", False):
        scopes += ["users:read", "users:write"]

    payload = {
        "sub": str(user.id), 
        "exp": expire,
        "scopes": scopes
    }
    token  = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}
