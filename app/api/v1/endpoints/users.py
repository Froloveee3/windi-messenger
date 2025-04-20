from typing import List

from fastapi import APIRouter, Security, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.schemas import UserCreate, UserRead
from app.models import User as AuthUser
from app.services import UserService
from app.api.deps import get_current_user
from app.db.session import get_db

router = APIRouter(tags=["users"])


@router.get(
    "/me",
    response_model=UserRead,
    summary="Current user information",
)
async def read_own_profile(
    current_user: AuthUser = Security(get_current_user, scopes=["me"]),
):
    return UserRead.model_validate(current_user)


@router.post(
    "/", 
    response_model=UserRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await UserService.create_user(db, user_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return UserRead.model_validate(user)


@router.get(
    "/", 
    response_model=List[UserRead],
    summary="List of all users (admin only)",
)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Security(get_current_user, scopes=["users:read"]),
):
    users = await UserService.list_users(db, skip=skip, limit=limit)
    return [UserRead.model_validate(u) for u in users]


@router.get(
    "/{user_id}", 
    response_model=UserRead,
    summary="Get user by ID (admin only)",
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Security(get_current_user, scopes=["users:read"]),
):
    try:
        user = await UserService.get_user(db, user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserRead.model_validate(user)


@router.post(
    "/{user_id}/promote",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Promote user to admin (admin only)",
)
async def promote_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AuthUser = Security(get_current_user, scopes=["users:write"]),
):
    try:
        await UserService.set_admin(db, user_id, True)
    except ValueError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/{user_id}/demote",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Demote user from admin (admin only)",
)
async def demote_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AuthUser = Security(get_current_user, scopes=["users:write"]),
):
    try:
        await UserService.set_admin(db, user_id, False)
    except ValueError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
