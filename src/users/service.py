from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.exceptions import HTTPException
from fastapi import status

from typing import Any

from src.users.schemas import UserUpdate
from src.users.constants import ErrorMessage
from src.users.models import User
from src.users import repository
from src.config import get_settings

settings = get_settings()

async def get_user_by_id(
    db: AsyncSession, 
    user_id: int
) -> User:

    user = await repository.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=ErrorMessage.USER_NOT_FOUND
        )
    return user  

async def get_users(
    db: AsyncSession,
    page: int = 1,
    page_size: int = settings.PAGINATION_PAGE_SIZE
) -> dict[str, Any]:

    users = await repository.get_users(
        db,
        page=page,
        page_size=page_size,
        limit=page_size + 1
    )

    return {
        "users": users[:page_size],
        "page": page,
        "page_size": page_size,
        "has_next": len(users) > page_size
    }

async def update_user(
    db: AsyncSession, 
    current_user: User,
    user_id: int,
    user_data: UserUpdate
) -> User:

    target_user = await get_user_by_id(db, user_id)
    if (target_user.id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorMessage.CANNOT_EDIT_ACCOUNT
        )

    data = user_data.model_dump(exclude_unset=True)

    for field, value in data.items():
        setattr(target_user, field, value)

    updated_user = await repository.update_user(
        db=db, 
        user=target_user,
    )

    await db.commit()
    await db.refresh(updated_user)

    return updated_user

async def delete_user(
    db: AsyncSession, 
    current_user: User,
    user_id: int
) -> bool:

    target_user = await get_user_by_id(db, user_id)
    
    if (current_user.id != target_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ErrorMessage.CANNOT_DELETE_ACCOUNT
        )

    if await repository.delete_user(db, user_id):
        await db.commit()
        return True
    return False