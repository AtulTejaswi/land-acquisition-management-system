"""Tests for report export endpoints (MIS, compensation, GIS parcels)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_mis_report_requires_auth(client: AsyncClient):
    """MIS report endpoint requires authentication."""
    resp = await client.get("/api/v1/reports/mis")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_compensation_report_requires_auth(client: AsyncClient):
    """Compensation report endpoint requires authentication."""
    resp = await client.get("/api/v1/reports/compensation")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_gis_parcels_report_requires_auth(client: AsyncClient):
    """GIS parcels report endpoint requires authentication."""
    resp = await client.get("/api/v1/reports/gis-parcels")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_mis_report_with_filters_requires_auth(client: AsyncClient):
    """MIS report with query filters requires authentication."""
    resp = await client.get(
        "/api/v1/reports/mis",
        params={"state_id": "00000000-0000-0000-0000-000000000001", "status": "active"},
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_compensation_report_with_filters_requires_auth(client: AsyncClient):
    """Compensation report with filters requires authentication."""
    resp = await client.get(
        "/api/v1/reports/compensation",
        params={"status": "assessed"},
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_gis_parcels_report_with_filters_requires_auth(client: AsyncClient):
    """GIS parcels report with filters requires authentication."""
    resp = await client.get(
        "/api/v1/reports/gis-parcels",
        params={"district_id": "00000000-0000-0000-0000-000000000001"},
    )
    assert resp.status_code in (401, 403)
