"""Tests for Phase 3 — Data Protection: encryption, masking, audit logging."""

import os
import pytest
from app.utils.encryption import encrypt_field, decrypt_field


class TestFieldEncryption:
    """Unit tests for the encrypt_field / decrypt_field utility."""

    def test_roundtrip(self):
        """Encrypted value can be decrypted back to original."""
        plaintext = "4321-5678-9012"
        ciphertext = encrypt_field(plaintext)
        assert ciphertext is not None
        assert ciphertext != plaintext
        assert decrypt_field(ciphertext) == plaintext

    def test_none_passthrough(self):
        """None input returns None for both encrypt and decrypt."""
        assert encrypt_field(None) is None
        assert decrypt_field(None) is None

    def test_different_ciphertexts(self):
        """Same plaintext encrypted twice produces different ciphertexts (random IV)."""
        a = encrypt_field("test-value")
        b = encrypt_field("test-value")
        assert a != b  # different ciphertexts
        assert decrypt_field(a) == decrypt_field(b) == "test-value"

    def test_empty_string(self):
        """Empty string is handled correctly."""
        ciphertext = encrypt_field("")
        assert decrypt_field(ciphertext) == ""

    def test_long_value(self):
        """Long values encrypt/decrypt correctly."""
        long_val = "A" * 1000
        assert decrypt_field(encrypt_field(long_val)) == long_val

    def test_unicode(self):
        """Unicode values (e.g., Hindi names) encrypt/decrypt correctly."""
        val = "गणेश वाघमरे"
        assert decrypt_field(encrypt_field(val)) == val
