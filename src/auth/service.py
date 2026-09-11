from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from fastapi import status

import logging
from datetime import datetime, timezone

from src.auth.security import (
    hash_secret,
    verify_secret, 
    hash_refresh_token,
    verify_refresh_token,
    create_access_token, 
    create_refresh_token,
    decode_refresh_token
)
from src.auth.schemas import RegisterRequest, ChangePassword
from src.auth.constants import ErrorMessage as AuthErrorMessage
from src.users.constants import ErrorMessage as UserErrorMessage
from src.users.repository import (
    insert_user,
    get_user_by_email, 
    get_user_by_id, 
    update_user
)
from src.users.models import User

logger = logging.getLogger(__name__)

async def register_user(
    db: AsyncSession,
    user_data: RegisterRequest
) -> User:

    if await get_user_by_email(db, user_data.email):
        raise HTTPException(
            detail=UserErrorMessage.EMAIL_EXISTS,
            status_code=status.HTTP_409_CONFLICT
        )

    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_secret(user_data.password)
    )

    user = await insert_user(db, user)
    await db.commit()

    return user

async def authenticate_user(
    db: AsyncSession, 
    email: str, 
    password: str
) -> dict[str, str]:
    
    user = await get_user_by_email(db, email)
    if not user or not verify_secret(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=AuthErrorMessage.INVALID_CREDENTIALS
        )

    user.last_login_at = datetime.now(timezone.utc)

    await update_user(db, user)
    await db.commit()
    
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = await _create_refresh_token(db, user)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

async def refresh_token(
    db: AsyncSession, 
    refresh_token: str
) -> dict[str, str]:
    
    payload = decode_refresh_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AuthErrorMessage.INVALID_CREDENTIALS
        )

    user_id = payload.get("sub")
    user = await get_user_by_id(db, int(user_id))

    if not verify_refresh_token(refresh_token, user.refresh_token_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AuthErrorMessage.INVALID_TOKEN
        )

    new_refresh_token = await _create_refresh_token(db, user)
    
    return {
        "access_token": create_access_token({"sub": str(user.id)}),
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

async def _create_refresh_token(
    db: AsyncSession,
    user: User,
) -> str:

    new_refresh_token = create_refresh_token({"sub": str(user.id)})
    user.refresh_token_hash = hash_refresh_token(new_refresh_token)

    _ = await update_user(
        db=db,
        user=user
    )

    await db.commit()

    return new_refresh_token

async def logout(db: AsyncSession, user: User) -> None:
    user.refresh_token_hash = None
    await db.commit()
    logger.info(f"User {user.id} logged out")

async def change_password(
    db: AsyncSession,
    current_user: User,
    change_password_data: ChangePassword
) -> None:

    target_user = await get_user_by_id(db, change_password_data.user_id)

    if current_user.id != target_user.id:
        raise HTTPException(
            detail=UserErrorMessage.CANNOT_CHANGE_PASSWORD,
            status_code=status.HTTP_403_FORBIDDEN
        )

    if not verify_secret(change_password_data.current_password, target_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=AuthErrorMessage.INCORRECT_PASSWORD
        )

    if not change_password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=AuthErrorMessage.MISSING_PASSWORD
        )

    target_user.password_hash = hash_secret(change_password_data.new_password)

    await db.commit()