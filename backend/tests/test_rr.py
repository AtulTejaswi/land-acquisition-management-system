import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_rr_families_unauthenticated(client: AsyncClient):
    """RR families endpoint without auth returns 401 or 403."""
    resp = await client.get("/api/v1/rr/families")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_rr_families_list_requires_auth(client: AsyncClient):
    """RR families list requires authentication."""
    resp = await client.get("/api/v1/rr/families")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_rr_summary_requires_auth(client: AsyncClient):
    """RR summary endpoint requires authentication."""
    resp = await client.get("/api/v1/rr/summary")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_rr_family_detail_404(client: AsyncClient):
    """RR family detail with invalid UUID returns 401 (no auth) or 404."""
    fake_id = "00000000-0000-0000-0000-000000000001"
    resp = await client.get(f"/api/v1/rr/families/{fake_id}")
    # Without auth, should be 401
    assert resp.status_code in (401, 403, 404)


@pytest.mark.asyncio
async def test_rr_create_requires_role(client: AsyncClient):
    """Creating an RR family requires proper role."""
    resp = await client.post(
        "/api/v1/rr/families",
        json={
            "project_id": "00000000-0000-0000-0000-000000000001",
            "family_head_name": "Test Family",
        },
    )
    assert resp.status_code in (401, 403)
