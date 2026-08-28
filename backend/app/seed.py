"""
NLAMS Seed Script — Populates database with real Odisha land-record data.
Run: python -m app.seed

Seeds:
  - Roles
  - Super admin user (created first so import can reference it)
  - Real land parcels from bhoomirashi.gov.in export (Khordha district)
  - Remaining demo users (created AFTER import so state/district exist)
"""

import asyncio
import os
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.state import State, District, Village
from app.models.user import User, Role
from app.db.base import Base


engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_tables():
    async with engine.begin() as conn:
        # Drop all tables with CASCADE to handle circular FK dependencies
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO nlams"))
        await conn.execute(text("GRANT ALL ON ALL TABLES IN SCHEMA public TO nlams"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        await conn.run_sync(Base.metadata.create_all)


async def seed():
    await create_tables()
    async with async_session() as db:
        print("🌱 Seeding database...")

        # ===== ROLES =====
        roles_data = [
            ("super_admin", "Super Admin — Central Ministry"),
            ("state_authority", "State Authority"),
            ("district_officer", "District Collector / LAO"),
            ("agency", "Project Implementing Agency"),
            ("field_officer", "Field Officer"),
            ("citizen", "Citizen / Land Owner"),
        ]
        roles = {}
        for name, desc in roles_data:
            r = Role(name=name, description=desc)
            db.add(r)
            await db.flush()
            roles[name] = r
        print(f"  ✅ {len(roles)} roles created")

        # ===== SUPER ADMIN (created first so import can reference created_by) =====
        password_hash = get_password_hash("password123")
        super_admin = User(
            full_name="Rajesh Kumar",
            email="rajesh@nlams.gov.in",
            phone="9876543210",
            password_hash=password_hash,
            role_id=roles["super_admin"].id,
        )
        db.add(super_admin)
        await db.flush()
        print("  ✅ Super admin created")

        # ===== ODISHA LAND DATA (from bhoomirashi import) =====
        # Import creates State, District, Villages, Project, Parcels, Owners
        xlsx_path = None
        for candidate in [
            os.environ.get("BHOOMIRASHI_XLSX", ""),
            str(Path(__file__).parent.parent / "[bhoomirashi_gov_in_auth_revamp_sdet1_cshtml_project_id_54637]_features (1).xlsx"),
            str(Path(__file__).parent.parent / "_bhoomirashi_gov_in_auth_revamp_sdet1_cshtml_project_id_54637__features.xlsx"),
            str(Path(__file__).parent / "[bhoomirashi_gov_in_auth_revamp_sdet1_cshtml_project_id_54637]_features (1).xlsx"),
            str(Path(__file__).parent / "_bhoomirashi_gov_in_auth_revamp_sdet1_cshtml_project_id_54637__features.xlsx"),
        ]:
            if candidate and Path(candidate).exists():
                xlsx_path = candidate
                break

        if xlsx_path:
            from app.scripts.import_bhoomirashi_xlsx import import_bhoomirashi
            result = await import_bhoomirashi(xlsx_path, db, truncate=True)
            print(f"  ✅ Imported {result['parcels_created']} parcels, {result['owners_created']} owners from bhoomirashi")
        else:
            print("  ⚠️ bhoomirashi xlsx not found — skipping land data import")
            print("     Place the xlsx in the repo root or backend dir, or set BHOOMIRASHI_XLSX env var")

        # ===== REMAINING USERS — Created AFTER import so State/District exist =====
        odisha_state = (await db.execute(
            select(State).where(State.code == "OD")
        )).scalar_one_or_none()
        khordha_district = None
        if odisha_state:
            khordha_district = (await db.execute(
                select(District).where(
                    District.state_id == odisha_state.id,
                    District.name == "Khordha",
                )
            )).scalar_one_or_none()

        od_id = odisha_state.id if odisha_state else None
        kh_id = khordha_district.id if khordha_district else None

        user_specs = [
            ("Anil Das", "anil@odisha.gov.in", "9876543212", "state_authority", od_id, None, None),
            ("Suresh Mohanty", "suresh@khordha.gov.in", "9876543216", "district_officer", od_id, kh_id, None),
            ("NHAI Project Office", "agency@nhai.gov.in", "9876543221", "agency", od_id, None, "National Highways Authority of India"),
            ("Rahul Pradhan", "rahul.f@nlams.gov.in", "9876543226", "field_officer", od_id, kh_id, None),
            ("Ganesh Pattnaik", "ganesh@email.com", "9876543232", "citizen", od_id, kh_id, None),
        ]

        created_users = []
        for full_name, email, phone, role_name, state_id, district_id, agency in user_specs:
            u = User(
                full_name=full_name,
                email=email,
                phone=phone,
                password_hash=password_hash,
                role_id=roles[role_name].id,
                state_id=state_id,
                district_id=district_id,
                agency_name=agency,
            )
            db.add(u)
            created_users.append(u)
        await db.flush()
        print(f"  ✅ {len(created_users)} users created")

        await db.commit()
        print("\n🎉 Database seeded successfully!")
        print("\n📋 Default Login Credentials:")
        print("=" * 60)
        print(f"{'Role':<20} {'Email':<35} {'Password':<15}")
        print("=" * 60)
        creds = [
            ("Super Admin", "rajesh@nlams.gov.in"),
            ("State Auth", "anil@odisha.gov.in"),
            ("District Officer", "suresh@khordha.gov.in"),
            ("Agency", "agency@nhai.gov.in"),
            ("Field Officer", "rahul.f@nlams.gov.in"),
            ("Citizen", "ganesh@email.com"),
        ]
        for role, email in creds:
            print(f"{role:<20} {email:<35} {'password123':<15}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed())
