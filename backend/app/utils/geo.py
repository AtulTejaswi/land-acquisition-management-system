"""GeoAlchemy2 geometry helpers for LandParcel.geom column."""

from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import shape, mapping
from typing import Optional, Any


def geom_column():
    """Return the GeoAlchemy2 Geometry column type for land_parcels.geom."""
    return Geometry("POLYGON", srid=4326)


def geojson_to_geom(geojson: Any) -> Optional[str]:
    """Convert a GeoJSON geometry dict/object to a WKT string for storage.

    Accepts:
      - A dict with 'type' and 'coordinates' (GeoJSON geometry)
      - A WKT string (returned as-is)
      - None (returned as-is)
    """
    if geojson is None:
        return None
    if isinstance(geojson, str):
        return geojson
    try:
        geom = shape(geojson)
        return from_shape(geom, srid=4326)
    except Exception:
        return None


def geom_to_geojson(geom_value) -> Optional[dict]:
    """Convert a GeoAlchemy2 geometry value to a GeoJSON geometry dict.

    Accepts the raw column value (WKBElement or similar).
    """
    if geom_value is None:
        return None
    try:
        shp = to_shape(geom_value)
        return mapping(shp)
    except Exception:
        return None
