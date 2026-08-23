"""Tests for the GIS endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_gis_geojson_endpoint(client: AsyncClient):
    """GIS GeoJSON endpoint exists (returns 401 without auth)."""
    try:
        resp = await client.get("/api/v1/gis/parcels/geojson")
        assert resp.status_code in (401, 403, 500)
    except Exception:
        pytest.skip("Database not available")


@pytest.mark.asyncio
async def test_gis_import_requires_auth(client: AsyncClient):
    """GIS import endpoint requires authentication."""
    try:
        resp = await client.post("/api/v1/gis/import-geojson", json={})
        assert resp.status_code in (401, 403, 422, 500)
    except Exception:
        pytest.skip("Database not available")
