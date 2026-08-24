import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_possession_list_unauthenticated(client: AsyncClient):
    """Possession list without auth returns 401."""
    resp = await client.get("/api/v1/possession")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_possession_list_requires_auth(client: AsyncClient):
    """Possession list requires authentication."""
    resp = await client.get("/api/v1/possession")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_possession_detail_requires_auth(client: AsyncClient):
    """Possession detail requires authentication."""
    fake_id = "00000000-0000-0000-0000-000000000001"
    resp = await client.get(f"/api/v1/possession/{fake_id}")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_possession_project_status_requires_auth(client: AsyncClient):
    """Possession project status requires authentication."""
    fake_id = "00000000-0000-0000-0000-000000000001"
    resp = await client.get(f"/api/v1/possession/project/{fake_id}/status")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_possession_create_requires_role(client: AsyncClient):
    """Creating a possession record requires proper role."""
    resp = await client.post(
        "/api/v1/possession",
        json={
            "parcel_id": "00000000-0000-0000-0000-000000000001",
            "possession_type": "physical",
            "remarks": "Test possession",
        },
    )
    assert resp.status_code in (401, 403)
