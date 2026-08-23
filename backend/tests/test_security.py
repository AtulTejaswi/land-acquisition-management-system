"""Tests for core security utilities (no database required)."""

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


def test_password_hash_and_verify():
    """Password hashing produces verifiable hashes."""
    password = "password123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_password_hash_uniqueness():
    """Same password produces different hashes (salt)."""
    h1 = get_password_hash("test")
    h2 = get_password_hash("test")
    assert h1 != h2  # Different salt each time


def test_access_token_create_and_decode():
    """Access tokens can be created and decoded."""
    data = {"sub": "user-123", "role": "super_admin"}
    token = create_access_token(data)
    assert isinstance(token, str)
    assert len(token) > 0

    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user-123"
    assert decoded["role"] == "super_admin"


def test_refresh_token_create_and_decode():
    """Refresh tokens can be created and decoded."""
    data = {"sub": "user-456", "role": "citizen"}
    token = create_refresh_token(data)
    assert isinstance(token, str)

    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user-456"
    assert decoded["role"] == "citizen"


def test_decode_invalid_token():
    """Invalid tokens return None."""
    result = decode_token("invalid.token.here")
    assert result is None


def test_decode_empty_token():
    """Empty token returns None."""
    result = decode_token("")
    assert result is None
