"""
Shared pytest fixtures for NLAMS backend tests.
Uses httpx.AsyncClient for async endpoint testing.
"""

import asyncio
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.db.base import Base
from app.core.config import settings
from app.core.security import create_access_token

# Use the test database URL from environment (set by CI) or fall back to a PostgreSQL local DB
TEST_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://nlams_test:nlams_test@localhost:5432/nlams_test",
)


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for all tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Create a test database engine."""
    eng = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session for each test."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def _make_auth_headers(role: str, user_id: str = "00000000-0000-0000-0000-000000000001") -> dict:
    """Create Authorization headers for a given role."""
    token = create_access_token(
        {
            "sub": user_id,
            "role": role,
            "state_id": None,
            "district_id": None,
        }
    )
    return {"Authorization": f"Bearer {token}"}


# ===== Authenticated client fixtures for each role =====

SUPER_ADMIN_HEADERS = _make_auth_headers("super_admin")
STATE_AUTHORITY_HEADERS = _make_auth_headers("state_authority")
DISTRICT_OFFICER_HEADERS = _make_auth_headers("district_officer")
AGENCY_HEADERS = _make_auth_headers("agency")
FIELD_OFFICER_HEADERS = _make_auth_headers("field_officer")
CITIZEN_HEADERS = _make_auth_headers("citizen")


@pytest_asyncio.fixture
async def super_admin_client() -> AsyncGenerator[AsyncClient, None]:
    """HTTP client authenticated as super_admin."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", headers=SUPER_ADMIN_HEADERS
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def state_authority_client() -> AsyncGenerator[AsyncClient, None]:
    """HTTP client authenticated as state_authority."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", headers=STATE_AUTHORITY_HEADERS
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def district_officer_client() -> AsyncGenerator[AsyncClient, None]:
    """HTTP client authenticated as district_officer."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", headers=DISTRICT_OFFICER_HEADERS
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def agency_client() -> AsyncGenerator[AsyncClient, None]:
    """HTTP client authenticated as agency."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", headers=AGENCY_HEADERS
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def field_officer_client() -> AsyncGenerator[AsyncClient, None]:
    """HTTP client authenticated as field_officer."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", headers=FIELD_OFFICER_HEADERS
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def citizen_client() -> AsyncGenerator[AsyncClient, None]:
    """HTTP client authenticated as citizen."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", headers=CITIZEN_HEADERS
    ) as ac:
        yield ac
