"""SMS notification service — abstracted behind an interface (per spec D7 pattern).

Supports ``SMS_PROVIDER=mock`` (default, for demo) or ``SMS_PROVIDER=msg91`` for
the MSG91 transactional SMS gateway. The real provider is only called when the
env var is set; the mock always succeeds.
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)


class SMSProvider(ABC):
    """Interface that every SMS adapter must satisfy."""

    @abstractmethod
    async def send(self, phone: str, message: str) -> bool:
        """Send an SMS. Returns True on success."""
        ...


class MockSMSProvider(SMSProvider):
    """Sandbox/demo provider — logs the message instead of sending."""

    async def send(self, phone: str, message: str) -> bool:
        logger.info("[SMS MOCK] To=%s  Body=%s", phone, message)
        return True


class MSG91SMSProvider(SMSProvider):
    """Real MSG91 transactional SMS gateway.

    Requires ``MSG91_API_KEY`` in the environment.
    """

    def __init__(self, api_key: str, sender_id: str = "NLAMS"):
        self.api_key = api_key
        self.sender_id = sender_id

    async def send(self, phone: str, message: str) -> bool:
        import httpx

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    "https://api.msg91.com/api/v5/flow/",
                    headers={"authkey": self.api_key, "Content-Type": "application/json"},
                    json={
                        "flow_id": os.environ.get("MSG91_FLOW_ID", ""),
                        "mobiles": f"91{phone}",
                        "VAR1": message,
                    },
                )
                ok = resp.status_code == 200
                if not ok:
                    logger.warning("MSG91 returned %s: %s", resp.status_code, resp.text)
                return ok
        except Exception as e:
            logger.error("MSG91 SMS failed: %s", e)
            return False


def get_sms_provider() -> SMSProvider:
    """Factory: return the configured SMS provider."""
    provider_name = os.environ.get("SMS_PROVIDER", "mock").lower()
    if provider_name == "msg91":
        api_key = os.environ.get("MSG91_API_KEY", "")
        if not api_key:
            logger.warning("SMS_PROVIDER=msg91 but MSG91_API_KEY is empty — falling back to mock")
            return MockSMSProvider()
        return MSG91SMSProvider(api_key)
    return MockSMSProvider()
