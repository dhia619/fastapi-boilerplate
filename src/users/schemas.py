from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="User name",
    )
    email: EmailStr = Field(
        ...,
        description="User email address",
    )
    password: str = Field(
        ...,
        min_length=5,
        description="User password",
    )

class UserRead(BaseModel):
    id: int
    username: str
    email: str
    last_login_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    refresh_token_hash: str | None = None

class ListUsersResponse(BaseModel):
    users: list[UserRead]
    page: int
    page_size: int
    has_next: bool