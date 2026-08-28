"""Add 'wet' to land_type_enum and latitude/longitude to villages

Revision ID: 004_landtype_wet_village_coords
Revises: 003_postgis_geometry
Create Date: 2026-08-28

"""
from alembic import op
import sqlalchemy as sa

revision = "004_landtype_wet_village_coords"
down_revision = "003_postgis_geometry"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add 'wet' value to the land_type_enum
    op.execute("ALTER TYPE land_type_enum ADD VALUE IF NOT EXISTS 'wet'")

    # Add latitude/longitude to villages
    op.add_column(
        "villages",
        sa.Column("latitude", sa.Numeric(10, 7), nullable=True),
    )
    op.add_column(
        "villages",
        sa.Column("longitude", sa.Numeric(10, 7), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("villages", "longitude")
    op.drop_column("villages", "latitude")
    # Note: PostgreSQL does not support removing values from an enum type.
    # The 'wet' value will remain in land_type_enum after downgrade.
