"""ML import staging tables

Revision ID: 005_ml_staging
Revises: 004_landtype_wet_village_coords
Create Date: 2026-08-28

"""
from alembic import op
import sqlalchemy as sa

revision = "005_ml_staging"
down_revision = "004_landtype_wet_village_coords"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "imported_land_details",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("source_file", sa.String(500), nullable=False),
        sa.Column("source_sno", sa.String(50), nullable=False),
        sa.Column("dedupe_key", sa.String(400), nullable=False),
        sa.Column("raw_district", sa.Text(), nullable=True),
        sa.Column("raw_sub_district", sa.Text(), nullable=True),
        sa.Column("raw_village", sa.Text(), nullable=True),
        sa.Column("raw_survey_number", sa.Text(), nullable=True),
        sa.Column("raw_area", sa.Text(), nullable=True),
        sa.Column("raw_description", sa.Text(), nullable=True),
        sa.Column("raw_land_type", sa.Text(), nullable=True),
        sa.Column("raw_land_nature", sa.Text(), nullable=True),
        sa.Column("raw_land_category", sa.Text(), nullable=True),
        sa.Column("raw_additional_details", sa.Text(), nullable=True),
        sa.Column("district_norm", sa.String(200), nullable=True),
        sa.Column("sub_district_norm", sa.String(200), nullable=True),
        sa.Column("village_norm", sa.String(200), nullable=True),
        sa.Column("survey_number_norm", sa.String(200), nullable=True),
        sa.Column("survey_number_head", sa.Integer(), nullable=True),
        sa.Column("is_compound_survey", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("area_hectares", sa.Numeric(12, 6), nullable=True),
        sa.Column("land_type_mapped", sa.String(50), nullable=True),
        sa.Column("land_type_mapped_ok", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("ownership_status_mapped", sa.String(50), nullable=True),
        sa.Column("ownership_status_mapped_ok", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("land_category", sa.String(100), nullable=True),
        sa.Column("land_nature_label", sa.String(50), nullable=True),
        sa.Column("party_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("dedupe_key", name="uq_imported_land_details_dedupe_key"),
    )
    op.create_index("ix_imported_land_details_source_file", "imported_land_details", ["source_file"])
    op.create_index("ix_imported_land_details_source_sno", "imported_land_details", ["source_sno"])
    op.create_index("ix_imported_land_details_village_norm", "imported_land_details", ["village_norm"])
    op.create_index("ix_imported_land_details_land_nature_label", "imported_land_details", ["land_nature_label"])

    op.create_table(
        "imported_land_parties",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("source_file", sa.String(500), nullable=False),
        sa.Column("source_sno", sa.String(50), nullable=False),
        sa.Column("dedupe_key", sa.String(600), nullable=False),
        sa.Column("raw_name", sa.Text(), nullable=True),
        sa.Column("raw_address", sa.Text(), nullable=True),
        sa.Column("raw_type", sa.Text(), nullable=True),
        sa.Column("raw_area", sa.Text(), nullable=True),
        sa.Column("name_norm", sa.String(400), nullable=True),
        sa.Column("address_norm", sa.Text(), nullable=True),
        sa.Column("party_type", sa.String(100), nullable=True),
        sa.Column("party_type_mapped_ok", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("area_hectares", sa.Numeric(12, 6), nullable=True),
        sa.Column("imported_detail_id", sa.dialects.postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("imported_land_details.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("dedupe_key", name="uq_imported_land_parties_dedupe_key"),
    )
    op.create_index("ix_imported_land_parties_source_file", "imported_land_parties", ["source_file"])
    op.create_index("ix_imported_land_parties_source_sno", "imported_land_parties", ["source_sno"])
    op.create_index("ix_imported_land_parties_imported_detail_id", "imported_land_parties", ["imported_detail_id"])


def downgrade() -> None:
    op.drop_table("imported_land_parties")
    op.drop_table("imported_land_details")
