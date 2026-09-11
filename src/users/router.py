from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.users.schemas import *
from src.users import service
from src.users.models import User
from src.dependencies import get_current_user
from src.config import get_settings
import src.auth.service as auth_service

settings = get_settings()

user_router = APIRouter()

@user_router.get("", response_model=ListUsersResponse)
async def list_users(
    page: int = Query(1),
    page_size: int = Query(settings.PAGINATION_PAGE_SIZE),
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    return await service.get_users(
        db=session,
        page=page,
        page_size=page_size
    )


@user_router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    return await service.get_user_by_id(db=session, user_id=user_id)


@user_router.post(
    "", 
    response_model=UserRead, 
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    payload: UserCreate,
    session: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    return await auth_service.register_user(
        db=session,
        user_data=payload
    )


@user_router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return await service.update_user(
        db=session,
        current_user=user,
        user_id=user_id,
        user_data=payload
    )


@user_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    await service.delete_user(
        db=session, 
        current_user=user,
        user_id=user_id
    )