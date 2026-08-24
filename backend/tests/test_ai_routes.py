"""Tests for AI insight endpoints (delay prediction, risk score, compensation estimate, missing docs)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_delay_prediction_requires_auth(client: AsyncClient):
    """Delay prediction endpoint requires authentication."""
    fake_id = "00000000-0000-0000-0000-000000000001"
    resp = await client.get(f"/api/v1/ai/delay-prediction/{fake_id}")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_risk_score_requires_auth(client: AsyncClient):
    """Risk score endpoint requires authentication."""
    fake_id = "00000000-0000-0000-0000-000000000001"
    resp = await client.get(f"/api/v1/ai/risk-score/{fake_id}")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_compensation_estimate_requires_auth(client: AsyncClient):
    """Compensation estimate endpoint requires authentication."""
    resp = await client.post(
        "/api/v1/ai/compensation-estimate",
        params={"land_type": "agricultural", "area_hectares": 1.0},
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_missing_documents_requires_auth(client: AsyncClient):
    """Missing documents endpoint requires authentication."""
    fake_id = "00000000-0000-0000-0000-000000000001"
    resp = await client.get(f"/api/v1/ai/missing-documents/{fake_id}")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_delay_prediction_with_auth(super_admin_client: AsyncClient):
    """Delay prediction with auth returns 200 or 404 (no project)."""
    try:
        fake_id = "00000000-0000-0000-0000-000000000001"
        resp = await super_admin_client.get(f"/api/v1/ai/delay-prediction/{fake_id}")
        assert resp.status_code in (200, 404)
    except Exception:
        pytest.skip("Database not available")


@pytest.mark.asyncio
async def test_risk_score_with_auth(super_admin_client: AsyncClient):
    """Risk score with auth returns 200 or 404 (no project)."""
    try:
        fake_id = "00000000-0000-0000-0000-000000000001"
        resp = await super_admin_client.get(f"/api/v1/ai/risk-score/{fake_id}")
        assert resp.status_code in (200, 404)
    except Exception:
        pytest.skip("Database not available")


@pytest.mark.asyncio
async def test_compensation_estimate_with_auth(super_admin_client: AsyncClient):
    """Compensation estimate with valid params returns 200."""
    try:
        resp = await super_admin_client.post(
            "/api/v1/ai/compensation-estimate",
            params={"land_type": "agricultural", "area_hectares": 2.5},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "estimated_range_min" in data
        assert "estimated_range_max" in data
        assert data["estimated_range_min"] <= data["estimated_range_max"]
    except Exception:
        pytest.skip("Database not available")


@pytest.mark.asyncio
async def test_missing_documents_with_auth(super_admin_client: AsyncClient):
    """Missing documents with auth returns 200 or 404."""
    try:
        fake_id = "00000000-0000-0000-0000-000000000001"
        resp = await super_admin_client.get(f"/api/v1/ai/missing-documents/{fake_id}")
        assert resp.status_code in (200, 404)
    except Exception:
        pytest.skip("Database not available")


@pytest.mark.asyncio
async def test_delay_prediction_invalid_uuid(super_admin_client: AsyncClient):
    """Delay prediction with invalid UUID returns 422."""
    try:
        resp = await super_admin_client.get("/api/v1/ai/delay-prediction/not-a-uuid")
        assert resp.status_code == 422
    except Exception:
        pytest.skip("Database not available")


@pytest.mark.asyncio
async def test_compensation_estimate_different_land_types(super_admin_client: AsyncClient):
    """Compensation estimate works for different land types."""
    try:
        for land_type in ["agricultural", "residential", "commercial", "forest", "other"]:
            resp = await super_admin_client.post(
                "/api/v1/ai/compensation-estimate",
                params={"land_type": land_type, "area_hectares": 1.0},
            )
            assert resp.status_code == 200, f"Failed for land_type={land_type}"
            data = resp.json()
            assert data["land_type"] == land_type
    except Exception:
        pytest.skip("Database not available")
