from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.db.session import get_db
from app.models.user import User, Role
from app.models.refresh_token import RefreshToken
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
)
from app.core.config import settings
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
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

limiter = Limiter(key_func=get_remote_address)

# ---------------------------------------------------------------------------
# Cookie configuration
# ---------------------------------------------------------------------------
COOKIE_SECURE = settings.ENVIRONMENT == "production"
COOKIE_SAMESITE = "lax"
ACCESS_COOKIE = "nlams_access_token"
REFRESH_COOKIE = "nlams_refresh_token"
ACCESS_MAX_AGE = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # seconds
REFRESH_MAX_AGE = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # seconds


def _set_auth_cookies(
    response: JSONResponse, access_token: str, refresh_token: str
) -> JSONResponse:
    """Set httpOnly, Secure, SameSite cookies for access and refresh tokens."""
    response.set_cookie(
        key=ACCESS_COOKIE,
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=ACCESS_MAX_AGE,
        path="/",
    )
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        max_age=REFRESH_MAX_AGE,
        path="/",
    )
    return response


def _clear_auth_cookies(response: JSONResponse) -> JSONResponse:
    """Clear auth cookies on logout."""
    response.delete_cookie(ACCESS_COOKIE, path="/")
    response.delete_cookie(REFRESH_COOKIE, path="/")
    return response


def _token_data(user: User) -> dict:
    """Build the common payload dict for tokens."""
    return {
        "sub": str(user.id),
        "role": user.role.name if user.role else "",
        "state_id": str(user.state_id) if user.state_id else None,
        "district_id": str(user.district_id) if user.district_id else None,
    }


async def _issue_refresh_token(db: AsyncSession, user: User) -> str:
    """Create a refresh token row and return the raw token string."""
    raw_token, jti, expires_at_iso = create_refresh_token(_token_data(user))
    rt = RefreshToken(
        user_id=user.id,
        jti=jti,
        token_hash=hash_token(raw_token),
        expires_at=datetime.fromisoformat(expires_at_iso),
    )
    db.add(rt)
    await db.flush()
    return raw_token


def _user_response(user: User) -> UserResponse:
    """Build a UserResponse from a loaded User model."""
    return UserResponse(
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


# ---------------------------------------------------------------------------
# POST /auth/login  — sets httpOnly cookies
# ---------------------------------------------------------------------------
@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # request param is required by slowapi decorator
    result = await db.execute(
        select(User)
        .where(User.email == login_data.email, User.is_active == True)
        .options(
            selectinload(User.role),
            selectinload(User.state),
            selectinload(User.district),
        )
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    user.last_login_at = datetime.now(timezone.utc)
    await db.flush()

    access_token = create_access_token(_token_data(user))
    refresh_token = await _issue_refresh_token(db, user)
    await db.commit()

    resp = JSONResponse(
        content={
            "user": _user_response(user).model_dump(mode="json"),
            "token_type": "bearer",
        }
    )
    _set_auth_cookies(resp, access_token, refresh_token)
    return resp


# ---------------------------------------------------------------------------
# POST /auth/refresh  — reads refresh_token from cookie OR body
# ---------------------------------------------------------------------------
@router.post("/refresh")
@limiter.limit("10/minute")
async def refresh_token(request: Request, db: AsyncSession = Depends(get_db)):
    # Prefer cookie; fall back to JSON body for backward compat
    raw_refresh = request.cookies.get(REFRESH_COOKIE)
    if not raw_refresh:
        try:
            body = await request.json()
            raw_refresh = body.get("refresh_token")
        except Exception:
            pass
    if not raw_refresh:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token provided"
        )

    payload = decode_token(raw_refresh)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    jti = payload.get("jti")
    user_id = payload.get("sub")
    token_hash_val = hash_token(raw_refresh)

    # Find the stored refresh token
    stored = None
    if jti:
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.jti == jti)
        )
        stored = result.scalar_one_or_none()
        if stored is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found",
            )
    else:
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash_val)
        )
        stored = result.scalar_one_or_none()

    if stored and stored.revoked_at is not None:
        # Token reuse detected — revoke all tokens for this user
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == stored.user_id)
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    if stored and stored.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )

    # Token rotation: revoke old, issue new
    if stored:
        stored.revoked_at = datetime.now(timezone.utc)
        await db.flush()

    result = await db.execute(
        select(User)
        .where(User.id == uuid.UUID(user_id), User.is_active == True)
        .options(selectinload(User.role))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    new_access = create_access_token(_token_data(user))
    new_refresh = await _issue_refresh_token(db, user)
    await db.commit()

    resp = JSONResponse(content={"token_type": "bearer"})
    _set_auth_cookies(resp, new_access, new_refresh)
    return resp


# ---------------------------------------------------------------------------
# POST /auth/logout  — clears cookies + revokes refresh token
# ---------------------------------------------------------------------------
@router.post("/logout")
async def logout(request: Request, db: AsyncSession = Depends(get_db)):
    """Revoke the current refresh token and clear cookies."""
    raw_refresh = request.cookies.get(REFRESH_COOKIE)
    if raw_refresh:
        payload = decode_token(raw_refresh)
        if payload:
            jti = payload.get("jti")
            if jti:
                await db.execute(
                    update(RefreshToken)
                    .where(RefreshToken.jti == jti)
                    .values(revoked_at=datetime.now(timezone.utc))
                )
                await db.commit()

    resp = JSONResponse(content={"message": "Logged out successfully"})
    _clear_auth_cookies(resp)
    return resp


# ---------------------------------------------------------------------------
# POST /auth/logout-all  — revokes ALL tokens + clears cookies
# ---------------------------------------------------------------------------
@router.post("/logout-all")
async def logout_all(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke ALL active refresh tokens for the current user (sign out everywhere)."""
    await db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.user_id == current_user.id,
            RefreshToken.revoked_at.is_(None),
        )
        .values(revoked_at=datetime.now(timezone.utc))
    )
    await db.commit()

    resp = JSONResponse(content={"message": "All sessions revoked"})
    _clear_auth_cookies(resp)
    return resp


# ---------------------------------------------------------------------------
# GET /auth/me  — reads access_token from cookie
# ---------------------------------------------------------------------------
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return _user_response(current_user)


# ---------------------------------------------------------------------------
# POST /auth/forgot-password  — OTP only in non-production
# ---------------------------------------------------------------------------
@router.post("/forgot-password", response_model=ForgotPasswordResponse)
@limiter.limit("3/minute")
async def forgot_password(
    request: Request, forgot_data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)
):
    # request param is required by slowapi decorator
    result = await db.execute(select(User).where(User.email == forgot_data.email))
    user = result.scalar_one_or_none()

    otp = "".join(random.choices(string.digits, k=6))

    # In production, the OTP would be sent via SMS/email (see SMS_PROVIDER config).
    # Only return OTP in the response for non-production environments (demo/sandbox).
    otp_in_response = otp if settings.ENVIRONMENT != "production" else None

    return ForgotPasswordResponse(
        message="OTP sent to your registered email/phone",
        otp=otp_in_response,
    )
