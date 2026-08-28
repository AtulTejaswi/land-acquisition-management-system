"""Tests for refresh token revocation, rotation, logout, and logout-all (Phase 2).

Requires a running PostgreSQL instance. Tests skip gracefully when unavailable.
"""

import pytest
import uuid
from datetime import datetime, timedelta, timezone
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_token,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User, Role


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

USER_ID = "00000000-0000-0000-0000-000000000001"


def _token_data(role: str = "citizen") -> dict:
    return {
        "sub": USER_ID,
        "role": role,
        "state_id": None,
        "district_id": None,
    }


async def _seed_user_and_token(db_session: AsyncSession, email: str, role_name: str):
    """Seed a test user and return (user, raw_token, jti)."""
    role = Role(name=role_name, description="test")
    db_session.add(role)
    await db_session.flush()

    user = User(
        id=uuid.UUID(USER_ID),
        full_name="Test User",
        email=email,
        phone=f"999999{hash(email) % 100000:05d}",
        password_hash="x",
        role_id=role.id,
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    raw_token, jti, expires_at_iso = create_refresh_token(_token_data())
    rt = RefreshToken(
        user_id=user.id,
        jti=jti,
        token_hash=hash_token(raw_token),
        expires_at=datetime.fromisoformat(expires_at_iso),
    )
    db_session.add(rt)
    await db_session.commit()
    return user, raw_token, jti


# ---------------------------------------------------------------------------
# Tests — require PostgreSQL
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_refresh_token_rotation(client: AsyncClient, db_session: AsyncSession):
    """POST /refresh issues a new token pair and revokes the old refresh token."""
    try:
        user, raw_token, jti = await _seed_user_and_token(
            db_session, "rot@test.com", "citizen_test_rot"
        )
    except Exception:
        pytest.skip("Database not available")

    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": raw_token},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("token_type") == "bearer"
    # New tokens are set as httpOnly cookies
    assert "nlams_access_token" in resp.cookies
    assert "nlams_refresh_token" in resp.cookies
    assert resp.cookies["nlams_refresh_token"] != raw_token

    # Old token should now be revoked in the DB
    result = await db_session.execute(
        select(RefreshToken).where(RefreshToken.jti == jti)
    )
    old_stored = result.scalar_one()
    assert old_stored.revoked_at is not None


@pytest.mark.asyncio
async def test_reuse_of_revoked_refresh_token_rejected(
    client: AsyncClient, db_session: AsyncSession
):
    """Reusing a revoked refresh token returns 401 and revokes ALL tokens for user."""
    try:
        user, raw_token, jti = await _seed_user_and_token(
            db_session, "reuse@test.com", "citizen_test_reuse"
        )
    except Exception:
        pytest.skip("Database not available")

    # Revoke the token
    result = await db_session.execute(
        select(RefreshToken).where(RefreshToken.jti == jti)
    )
    stored = result.scalar_one()
    stored.revoked_at = datetime.now(timezone.utc)
    await db_session.commit()

    # Try to use the revoked token
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": raw_token},
    )
    assert resp.status_code == 401

    # ALL tokens for this user should now be revoked
    result2 = await db_session.execute(
        select(RefreshToken).where(RefreshToken.user_id == user.id)
    )
    all_tokens = result2.scalars().all()
    assert all(t.revoked_at is not None for t in all_tokens)


@pytest.mark.asyncio
async def test_expired_refresh_token_rejected(
    client: AsyncClient, db_session: AsyncSession
):
    """An expired refresh token returns 401."""
    try:
        user, raw_token, jti = await _seed_user_and_token(
            db_session, "expired@test.com", "citizen_test_expired"
        )
    except Exception:
        pytest.skip("Database not available")

    # Overwrite with an already-expired token
    result = await db_session.execute(
        select(RefreshToken).where(RefreshToken.jti == jti)
    )
    stored = result.scalar_one()
    stored.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
    await db_session.commit()

    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": raw_token},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_logout_revokes_single_token(
    client: AsyncClient, db_session: AsyncSession
):
    """POST /logout revokes the specified refresh token."""
    try:
        user, raw_token, jti = await _seed_user_and_token(
            db_session, "logout@test.com", "citizen_test_logout"
        )
    except Exception:
        pytest.skip("Database not available")

    resp = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": raw_token},
    )
    assert resp.status_code == 200
    assert resp.json()["message"] == "Logged out successfully"

    # Verify it's revoked in DB
    result = await db_session.execute(
        select(RefreshToken).where(RefreshToken.jti == jti)
    )
    stored = result.scalar_one()
    assert stored is not None
    assert stored.revoked_at is not None


@pytest.mark.asyncio
async def test_logout_all_revokes_all_user_tokens(
    client: AsyncClient, db_session: AsyncSession
):
    """POST /logout-all revokes every active refresh token for the authenticated user."""
    try:
        user, _, _ = await _seed_user_and_token(
            db_session, "logoutall@test.com", "citizen_test_logoutall"
        )
    except Exception:
        pytest.skip("Database not available")

    # Create a second refresh token for same user
    raw2, jti2, exp2 = create_refresh_token(_token_data())
    rt2 = RefreshToken(
        user_id=user.id, jti=jti2, token_hash=hash_token(raw2),
        expires_at=datetime.fromisoformat(exp2),
    )
    db_session.add(rt2)
    await db_session.commit()

    # Use access token to call /logout-all
    access_token = create_access_token(_token_data())
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = await client.post("/api/v1/auth/logout-all", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["message"] == "All sessions revoked"

    # Both tokens should be revoked
    result = await db_session.execute(
        select(RefreshToken).where(RefreshToken.user_id == user.id)
    )
    all_tokens = result.scalars().all()
    assert len(all_tokens) == 2
    assert all(t.revoked_at is not None for t in all_tokens)


# ---------------------------------------------------------------------------
# Tests — no database required
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_refresh_missing_fields(client: AsyncClient):
    """POST /refresh with empty body and no cookie returns 401."""
    resp = await client.post("/api/v1/auth/refresh", json={})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    """POST /refresh with garbage token returns 401."""
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "not.a.valid.token"},
    )
    assert resp.status_code == 401
