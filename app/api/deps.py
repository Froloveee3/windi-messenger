from typing import List
from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt, JWTError

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.db.session import get_db
from app.models import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
    scopes=settings.SCOPES
)


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        token_scopes: List[str] = payload.get("scopes", [])
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    
    res = await db.execute(select(User).where(User.id == int(user_id)))
    user = res.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_ws(
    websocket: WebSocket,
    security_scopes: SecurityScopes,
    db: AsyncSession = Depends(get_db),
) -> User:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        token_scopes: List[str] = payload.get("scopes", [])
        if user_id is None:
            raise JWTError()
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    res = await db.execute(select(User).where(User.id == int(user_id)))
    user = res.scalar_one_or_none()
    if user is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    return user
