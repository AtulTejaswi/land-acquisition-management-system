"""Tests for security configuration (SECRET_KEY enforcement)."""

import pytest
import os
from unittest.mock import patch


def test_secret_key_required_in_production():
    """App raises ValueError if SECRET_KEY is empty in production."""
    from app.core.config import Settings, _validate_settings

    settings = Settings(ENVIRONMENT="production", SECRET_KEY="")
    with pytest.raises(ValueError, match="SECRET_KEY environment variable is required"):
        _validate_settings(settings)


def test_secret_key_auto_generated_in_development():
    """App auto-generates a key in development when not set."""
    from app.core.config import Settings, _validate_settings

    settings = Settings(ENVIRONMENT="development", SECRET_KEY="")
    result = _validate_settings(settings)
    assert len(result.SECRET_KEY) > 20  # Should be a reasonable length


def test_secret_key_preserved_when_set():
    """App preserves explicitly set SECRET_KEY."""
    from app.core.config import Settings, _validate_settings

    my_key = "my-custom-secret-key-for-testing"
    settings = Settings(ENVIRONMENT="production", SECRET_KEY=my_key)
    result = _validate_settings(settings)
    assert result.SECRET_KEY == my_key


def test_settings_load_from_env():
    """Settings can be loaded from environment variables."""
    from app.core.config import Settings

    with patch.dict(os.environ, {"SECRET_KEY": "test-env-key", "ENVIRONMENT": "test"}):
        settings = Settings()
        assert settings.SECRET_KEY == "test-env-key"
        assert settings.ENVIRONMENT == "test"
