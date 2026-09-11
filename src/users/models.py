from sqlalchemy import Column, Integer, DateTime, String, Boolean, func

from src.database import SQLAlchemyBase

class User(SQLAlchemyBase):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    refresh_token_hash = Column(String, unique=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True))

    is_verified = Column(Boolean, nullable=False, default=False)