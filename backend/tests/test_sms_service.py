"""Tests for the SMS service interface (Phase 7)."""

import pytest
from app.services.sms import MockSMSProvider, MSG91SMSProvider, get_sms_provider


class TestMockSMSProvider:
    @pytest.mark.asyncio
    async def test_mock_send_returns_true(self):
        provider = MockSMSProvider()
        result = await provider.send("9876543210", "Test OTP: 123456")
        assert result is True

    @pytest.mark.asyncio
    async def test_mock_send_empty_phone(self):
        provider = MockSMSProvider()
        result = await provider.send("", "Test message")
        assert result is True


class TestSMSProviderFactory:
    def test_default_returns_mock(self):
        provider = get_sms_provider()
        assert isinstance(provider, MockSMSProvider)

    def test_mock_env_returns_mock(self, monkeypatch):
        monkeypatch.setenv("SMS_PROVIDER", "mock")
        provider = get_sms_provider()
        assert isinstance(provider, MockSMSProvider)

    def test_msg91_without_key_falls_back_to_mock(self, monkeypatch):
        monkeypatch.setenv("SMS_PROVIDER", "msg91")
        monkeypatch.delenv("MSG91_API_KEY", raising=False)
        provider = get_sms_provider()
        assert isinstance(provider, MockSMSProvider)

    def test_msg91_with_key_returns_msg91(self, monkeypatch):
        monkeypatch.setenv("SMS_PROVIDER", "msg91")
        monkeypatch.setenv("MSG91_API_KEY", "test-api-key")
        provider = get_sms_provider()
        assert isinstance(provider, MSG91SMSProvider)
