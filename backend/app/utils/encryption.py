"""Fernet-based encryption for sensitive data fields (Phase 3).

Uses a symmetric key from ENCRYPTION_KEY env var. If unset in dev mode, generates
an ephemeral key (fields will not survive restarts). In production, ENCRYPTION_KEY
is mandatory.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_fernet = None


def _get_fernet():
    """Lazy-initialize the Fernet cipher."""
    global _fernet
    if _fernet is not None:
        return _fernet

    key = os.environ.get("ENCRYPTION_KEY", "")
    if not key:
        from app.core.config import settings

        if settings.ENVIRONMENT == "production":
            raise ValueError(
                "ENCRYPTION_KEY is required in production. "
                'Generate one with: python -c "from cryptography.fernet import Fernet; '
                'print(Fernet.generate_key().decode())"'
            )
        else:
            from cryptography.fernet import Fernet

            key = Fernet.generate_key().decode()
            os.environ["ENCRYPTION_KEY"] = key
            logger.warning(
                "⚠️  No ENCRYPTION_KEY set — auto-generating ephemeral dev key. "
                "Sensitive fields will not survive restarts. "
                "Set ENCRYPTION_KEY in .env for persistent encryption."
            )

    from cryptography.fernet import Fernet

    _fernet = Fernet(key.encode() if isinstance(key, str) else key)
    return _fernet


def encrypt_field(plaintext: Optional[str]) -> Optional[str]:
    """Encrypt a plaintext string. Returns None if input is None."""
    if plaintext is None:
        return None
    f = _get_fernet()
    return f.encrypt(plaintext.encode()).decode()


def decrypt_field(ciphertext: Optional[str]) -> Optional[str]:
    """Decrypt a ciphertext string. Returns None if input is None."""
    if ciphertext is None:
        return None
    f = _get_fernet()
    return f.decrypt(ciphertext.encode()).decode()
