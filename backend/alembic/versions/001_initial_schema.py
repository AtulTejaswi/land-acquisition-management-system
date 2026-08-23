"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-08-23

"""
from alembic import op
import sqlalchemy as sa

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    op.execute("""
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """)

    # States
    op.create_table("states",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("code", sa.String(10), nullable=False, unique=True),
        sa.Column("region", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_states_id", "states", ["id"])

    # Districts
    op.create_table("districts",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("state_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("states.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(10), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("state_id", "name"),
    )
    op.create_index("ix_districts_state", "districts", ["state_id"])

    # Villages
    op.create_table("villages",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("district_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("districts.id"), nullable=False),
        sa.Column("tehsil", sa.String(100), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_villages_district", "villages", ["district_id"])

    # Roles
    op.create_table("roles",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(50), nullable=False, unique=True),
        sa.Column("description", sa.String(255), nullable=True),
    )

    # Ministries
    op.create_table("ministries",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
    )

    # Project Categories
    op.create_table("project_categories",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(100), nullable=False),
    )

    # Users
    op.create_table("users",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(200), nullable=False, unique=True),
        sa.Column("phone", sa.String(15), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("state_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("states.id"), nullable=True),
        sa.Column("district_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("districts.id"), nullable=True),
        sa.Column("agency_name", sa.String(200), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_phone", "users", ["phone"], unique=True)
    op.create_index("ix_users_role", "users", ["role_id"])
    op.create_index("ix_users_state", "users", ["state_id"])
    op.create_index("ix_users_district", "users", ["district_id"])

    # Projects
    op.create_table("projects",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("ministry_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("ministries.id"), nullable=False),
        sa.Column("category_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("project_categories.id"), nullable=False),
        sa.Column("implementing_agency_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("state_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("states.id"), nullable=False),
        sa.Column("district_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("districts.id"), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("dpr_document_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("estimated_budget", sa.Numeric(18, 2), nullable=True),
        sa.Column("estimated_land_required_hectares", sa.Numeric(12, 3), nullable=True),
        sa.Column("priority", sa.String(20), server_default="medium", nullable=False),
        sa.Column("current_stage", sa.String(50), server_default="project_proposal", nullable=False),
        sa.Column("status", sa.String(20), server_default="draft", nullable=False),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("target_completion_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_projects_state_district_status", "projects", ["state_id", "district_id", "status"])
    op.create_index("idx_projects_name_ft", "projects", sa.text("name gin_trgm_ops"), postgresql_using="gin")

    # Milestones
    op.create_table("milestones",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stage", sa.String(50), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("planned_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("responsible_officer_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("remarks", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_milestones_project", "milestones", ["project_id"])

    # Land Parcels
    op.create_table("land_parcels",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("survey_number", sa.String(50), nullable=False),
        sa.Column("village_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("villages.id"), nullable=False),
        sa.Column("district_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("districts.id"), nullable=False),
        sa.Column("state_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("states.id"), nullable=False),
        sa.Column("area_hectares", sa.Numeric(12, 4), nullable=True),
        sa.Column("geom", sa.Text, nullable=True),
        sa.Column("land_type", sa.String(30), server_default="agricultural", nullable=False),
        sa.Column("ownership_status", sa.String(20), server_default="private", nullable=False),
        sa.Column("verification_status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_parcels_project", "land_parcels", ["project_id"])
    op.create_index("idx_parcels_geom", "land_parcels", [sa.text("geom")], postgresql_using="gist")

    # Land Owners
    op.create_table("land_owners",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("parcel_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("land_parcels.id"), nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("aadhaar_masked", sa.String(20), nullable=True),
        sa.Column("phone", sa.String(15), nullable=False),
        sa.Column("email", sa.String(200), nullable=True),
        sa.Column("bank_account_masked", sa.String(20), nullable=True),
        sa.Column("ifsc", sa.String(20), nullable=True),
        sa.Column("share_percentage", sa.Numeric(5, 2), nullable=True),
        sa.Column("user_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_land_owners_name_ft", "land_owners", sa.text("full_name gin_trgm_ops"), postgresql_using="gin")

    # Survey Records
    op.create_table("survey_records",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("parcel_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("land_parcels.id"), nullable=False),
        sa.Column("surveyed_by", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("survey_date", sa.String(30), nullable=True),
        sa.Column("geo_lat", sa.Numeric(10, 7), nullable=True),
        sa.Column("geo_lng", sa.Numeric(10, 7), nullable=True),
        sa.Column("condition_notes", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), server_default="scheduled", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Circle Rates
    op.create_table("circle_rates",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("state_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("states.id"), nullable=False),
        sa.Column("district_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("districts.id"), nullable=True),
        sa.Column("land_type", sa.String(30), nullable=False),
        sa.Column("rate_per_hectare", sa.Numeric(18, 2), nullable=False),
        sa.Column("financial_year", sa.String(10), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Legal Notifications
    op.create_table("legal_notifications",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("section_type", sa.String(50), nullable=False),
        sa.Column("notification_number", sa.String(100), nullable=True),
        sa.Column("issued_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_document_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=True),
        sa.Column("status", sa.String(20), server_default="draft", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Objections
    op.create_table("objections",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("parcel_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("land_parcels.id"), nullable=False),
        sa.Column("filed_by", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("filer_name", sa.String(200), nullable=False),
        sa.Column("filer_contact", sa.String(15), nullable=True),
        sa.Column("objection_text", sa.Text, nullable=False),
        sa.Column("hearing_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), server_default="filed", nullable=False),
        sa.Column("resolution_remarks", sa.Text, nullable=True),
        sa.Column("resolved_by", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Compensation
    op.create_table("compensation",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("parcel_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("land_parcels.id"), nullable=False),
        sa.Column("market_value", sa.Numeric(18, 2), nullable=True),
        sa.Column("solatium", sa.Numeric(18, 2), nullable=True),
        sa.Column("additional_compensation", sa.Numeric(18, 2), nullable=True),
        sa.Column("total_award", sa.Numeric(18, 2), nullable=True),
        sa.Column("assessed_by", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("assessment_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), server_default="draft", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Payments
    op.create_table("payments",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("compensation_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("compensation.id"), nullable=False),
        sa.Column("land_owner_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("land_owners.id"), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("pfms_reference", sa.String(100), nullable=True),
        sa.Column("bank_verification_status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("payment_status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("disbursed_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Possession
    op.create_table("possession",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("parcel_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("land_parcels.id"), nullable=False),
        sa.Column("possession_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("taken_by", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("possession_type", sa.String(20), nullable=True),
        sa.Column("remarks", sa.Text, nullable=True),
        sa.Column("document_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Rehabilitation Families
    op.create_table("rehabilitation_families",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("family_head_name", sa.String(200), nullable=False),
        sa.Column("family_id_number", sa.String(50), nullable=True),
        sa.Column("member_count", sa.Integer, nullable=True),
        sa.Column("displaced_status", sa.String(30), server_default="not_displaced", nullable=False),
        sa.Column("housing_benefit_status", sa.String(30), server_default="not_started", nullable=False),
        sa.Column("employment_benefit_status", sa.String(30), server_default="not_started", nullable=False),
        sa.Column("monetary_benefit_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("current_stage", sa.String(30), server_default="identification", nullable=False),
        sa.Column("progress_percentage", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Documents (create before legal_notifications FK reference)
    op.create_table("documents",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=True),
        sa.Column("parcel_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("land_parcels.id"), nullable=True),
        sa.Column("uploaded_by", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("doc_type", sa.String(30), nullable=False),
        sa.Column("file_name", sa.String(500), nullable=False),
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column("file_size", sa.Integer, nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("version", sa.Integer, server_default="1"),
        sa.Column("parent_document_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id"), nullable=True),
        sa.Column("digital_signature_placeholder", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Audit Logs
    op.create_table("audit_logs",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("performed_by", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("old_value", sa.dialects.postgresql.JSONB, nullable=True),
        sa.Column("new_value", sa.dialects.postgresql.JSONB, nullable=True),
        sa.Column("remarks", sa.Text, nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Notifications
    op.create_table("notifications",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("type", sa.String(20), server_default="info", nullable=False),
        sa.Column("channel", sa.String(20), server_default="in_app", nullable=False),
        sa.Column("is_read", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("related_entity_type", sa.String(50), nullable=True),
        sa.Column("related_entity_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("audit_logs")
    op.drop_table("documents")
    op.drop_table("rehabilitation_families")
    op.drop_table("possession")
    op.drop_table("payments")
    op.drop_table("compensation")
    op.drop_table("objections")
    op.drop_table("legal_notifications")
    op.drop_table("circle_rates")
    op.drop_table("survey_records")
    op.drop_table("land_owners")
    op.drop_index("idx_parcels_geom", table_name="land_parcels")
    op.drop_table("land_parcels")
    op.drop_table("milestones")
    op.drop_index("idx_projects_name_ft", table_name="projects")
    op.drop_index("idx_projects_state_district_status", table_name="projects")
    op.drop_table("projects")
    op.drop_table("users")
    op.drop_table("project_categories")
    op.drop_table("ministries")
    op.drop_table("roles")
    op.drop_table("villages")
    op.drop_table("districts")
    op.drop_table("states")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
