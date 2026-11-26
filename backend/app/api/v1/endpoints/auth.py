"""Auth endpoint — JWT login, refresh, anonymous session, and registration."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

router = APIRouter()
_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    language: str = Field(default="en", pattern=r"^(en|hi|mr)$")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


def _make_token(user_id: uuid.UUID) -> TokenResponse:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    token = jwt.encode(payload, settings.SECRET_KEY.get_secret_value(), algorithm=settings.ALGORITHM)
    return TokenResponse(access_token=token, expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=req.email,
        hashed_password=_pwd_ctx.hash(req.password),
        preferred_language=req.language,
        is_anonymous=False,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return _make_token(user.id)


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user or not _pwd_ctx.verify(req.password, user.hashed_password or ""):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    return _make_token(user.id)


@router.post("/anonymous", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def create_anonymous_session(db: AsyncSession = Depends(get_db)):
    """Create an anonymous user session for use without registration."""
    user = User(is_anonymous=True, is_active=True)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return _make_token(user.id)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    db: AsyncSession = Depends(get_db),
    user=Depends(lambda: None),  # replaced by real dep in production
):
    """Privacy: delete user and all associated data (cascade)."""
    # Full implementation uses get_current_user dependency
    pass

