"""Tests for the health check and core app endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Health endpoint returns 200 with service info."""
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "NLAMS API"
    assert "version" in data


@pytest.mark.asyncio
async def test_openapi_docs(client: AsyncClient):
    """FastAPI auto-generated docs are accessible."""
    resp = await client.get("/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    assert "paths" in schema
    assert "/api/health" in schema["paths"]


@pytest.mark.asyncio
async def test_nonexistent_route_returns_404(client: AsyncClient):
    """Unknown routes return 404."""
    resp = await client.get("/api/v1/this-does-not-exist")
    assert resp.status_code == 404
