from pydantic import BaseModel, Field

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

class RefreshRequest(BaseModel):
    refresh_token: str

class ChangePassword(BaseModel):
    user_id: int = Field(
        ...,
        description="User id"
    )
    current_password: str = Field(
        ...,
        min_length=5,
        description="Current user password",
    )
    new_password: str = Field(
        ...,
        min_length=5,
        description="New user password",
    )