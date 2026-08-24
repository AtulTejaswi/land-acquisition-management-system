from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.db.session import get_db
from app.models.user import User, Role
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.deps import get_current_user
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    UserResponse,
    UserCreate,
    UserUpdate,
)
import uuid
import random
import string

router = APIRouter(prefix="/auth", tags=["auth"])

limiter = Limiter(key_func=get_remote_address)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # request param is required by slowapi decorator
    result = await db.execute(
        select(User).where(User.email == login_data.email, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    token_data = {
        "sub": str(user.id),
        "role": user.role.name if user.role else "",
        "state_id": str(user.state_id) if user.state_id else None,
        "district_id": str(user.district_id) if user.district_id else None,
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    user_response = UserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        role_name=user.role.name if user.role else "",
        state_id=user.state_id,
        state_name=user.state.name if user.state else None,
        district_id=user.district_id,
        district_name=user.district.name if user.district else None,
        agency_name=user.agency_name,
        is_active=user.is_active,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_response,
    )


@router.post("/refresh", response_model=dict)
async def refresh_token(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    user_id = payload.get("sub")
    result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id), User.is_active == True)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    token_data = {
        "sub": str(user.id),
        "role": user.role.name if user.role else "",
        "state_id": str(user.state_id) if user.state_id else None,
        "district_id": str(user.district_id) if user.district_id else None,
    }
    return {
        "access_token": create_access_token(token_data),
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        phone=current_user.phone,
        role_name=current_user.role.name if current_user.role else "",
        state_id=current_user.state_id,
        state_name=current_user.state.name if current_user.state else None,
        district_id=current_user.district_id,
        district_name=current_user.district.name if current_user.district else None,
        agency_name=current_user.agency_name,
        is_active=current_user.is_active,
    )


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
@limiter.limit("3/minute")
async def forgot_password(
    request: Request, forgot_data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)
):
    # request param is required by slowapi decorator
    result = await db.execute(select(User).where(User.email == forgot_data.email))
    user = result.scalar_one_or_none()
    # Always return success for security
    otp = "".join(random.choices(string.digits, k=6))
    # In demo mode, include OTP in response
    return ForgotPasswordResponse(
        message="OTP sent to your registered email/phone",
        otp=otp,  # Demo mode: show OTP
    )
