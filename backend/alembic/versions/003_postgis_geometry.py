"""Convert land_parcels.geom from TEXT to PostGIS GEOMETRY (Phase 1)

Revision ID: 003_postgis_geometry
Revises: 002_refresh_tokens
Create Date: 2026-08-25

"""
from alembic import op
import sqlalchemy as sa

revision = "003_postgis_geometry"
down_revision = "002_refresh_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add a temporary geometry column
    op.execute(
        "ALTER TABLE land_parcels ADD COLUMN geom_new GEOMETRY(Polygon, 4326)"
    )

    # Convert existing TEXT/JSON data to real geometries.
    # The seed script stores str(dict) which Python repr's; also handle
    # proper GeoJSON strings.
    op.execute(
        """
        UPDATE land_parcels
        SET geom_new = CASE
            WHEN geom IS NOT NULL AND geom != '' THEN
                ST_GeomFromGeoJSON(geom::json)
            ELSE NULL
        END
        WHERE geom IS NOT NULL AND geom != ''
        """
    )

    # Drop old column and rename new one
    op.execute("ALTER TABLE land_parcels DROP COLUMN geom")
    op.execute("ALTER TABLE land_parcels RENAME COLUMN geom_new TO geom")

    # Recreate GiST spatial index
    op.create_index("idx_parcels_geom", "land_parcels", ["geom"], postgresql_using="gist")


def downgrade() -> None:
    op.drop_index("idx_parcels_geom", table_name="land_parcels")

    # Convert back to TEXT (GeoJSON strings)
    op.execute(
        "ALTER TABLE land_parcels ADD COLUMN geom_old TEXT"
    )
    op.execute(
        """
        UPDATE land_parcels
        SET geom_old = ST_AsGeoJSON(geom)::text
        WHERE geom IS NOT NULL
        """
    )
    op.execute("ALTER TABLE land_parcels DROP COLUMN geom")
    op.execute("ALTER TABLE land_parcels RENAME COLUMN geom_old TO geom")
