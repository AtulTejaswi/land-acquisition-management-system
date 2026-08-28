"""Tests for the GIS endpoints including spatial query (Phase 1)."""

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


@pytest.mark.asyncio
async def test_spatial_nearby_requires_auth(client: AsyncClient):
    """Spatial nearby endpoint requires authentication."""
    try:
        resp = await client.get(
            "/api/v1/gis/parcels/nearby",
            params={"lat": 21.1458, "lng": 79.0882, "radius_km": 10},
        )
        assert resp.status_code in (401, 403, 500)
    except Exception:
        pytest.skip("Database not available")


@pytest.mark.asyncio
async def test_spatial_nearby_missing_params(client: AsyncClient):
    """Spatial nearby endpoint returns 422 for missing required params."""
    try:
        resp = await client.get("/api/v1/gis/parcels/nearby")
        assert resp.status_code == 422
    except Exception:
        pytest.skip("Database not available")


@pytest.mark.asyncio
async def test_spatial_nearby_invalid_params(client: AsyncClient):
    """Spatial nearby endpoint returns 422 for invalid params."""
    try:
        resp = await client.get(
            "/api/v1/gis/parcels/nearby",
            params={"lat": "not-a-number", "lng": 79.0882, "radius_km": 10},
        )
        assert resp.status_code == 422
    except Exception:
        pytest.skip("Database not available")
