"""
NLAMS Seed Script — Populates database with realistic Indian data for hackathon demo.
Run: python -m app.seed
"""

import asyncio
import uuid
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.state import State, District, Village
from app.models.user import User, Role
from app.models.project import (
    Ministry,
    ProjectCategory,
    Project,
    Milestone,
    ProjectStatus,
    ProjectPriority,
    MilestoneStatus,
    STAGES,
)
from app.models.land import (
    LandParcel,
    LandOwner,
    SurveyRecord,
    LandType,
    OwnershipStatus,
    VerificationStatus,
)
from app.models.compensation import Compensation, Payment
from app.models.possession import Possession
from app.models.rr import RehabilitationFamily
from app.models.legal import LegalNotification
from app.models.document import Document
from app.models.audit import AuditLog
from app.models.notification import NotificationApp
from app.models.circle_rate import CircleRate
from app.db.base import Base


engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_tables():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        await conn.run_sync(Base.metadata.drop_all)
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

        # ===== STATES & DISTRICTS =====
        states_data = [
            (
                "Maharashtra",
                "MH",
                "West",
                [
                    ("Nagpur", "NGP", ["Kamptee", "Hingna", "Parseoni", "Saoner", "Ramtek"]),
                    ("Mumbai", "MUM", ["Andheri", "Borivali", "Thane", "Kalyan", "Ulhasnagar"]),
                    ("Pune", "PUN", ["Haveli", "Baramati", "Indapur", "Shirur", "Mulshi"]),
                ],
            ),
            (
                "Madhya Pradesh",
                "MP",
                "Central",
                [
                    ("Bhopal", "BPL", ["Huzur", "Berasia", "Sehore", "Mandideep", "Raisen"]),
                    ("Indore", "IND", ["Mhow", "Depalpur", "Sanwer", "Barwaha", "Pithampur"]),
                    ("Betul", "BET", ["Betul", "Multai", "Amla", "Bhainsdehi", "Chicholi"]),
                ],
            ),
            (
                "Tamil Nadu",
                "TN",
                "South",
                [
                    ("Chennai", "CHE", ["Tondiarpet", "Mylapore", "Adyar", "Tambaram", "Ambattur"]),
                    (
                        "Coimbatore",
                        "CJB",
                        ["Pollachi", "Mettupalayam", "Sulur", "Kinathukadavu", "Valparai"],
                    ),
                ],
            ),
            (
                "Uttar Pradesh",
                "UP",
                "North",
                [
                    (
                        "Lucknow",
                        "LKO",
                        ["Lucknow", "Mohanlalganj", "Bakshi Ka Talaab", "Sarojini Nagar", "Mal"],
                    ),
                    (
                        "Varanasi",
                        "VNS",
                        ["Varanasi", "Ramnagar", "Pindra", "Arajiline", "Cholapur"],
                    ),
                ],
            ),
            (
                "Gujarat",
                "GJ",
                "West",
                [
                    (
                        "Ahmedabad",
                        "AMD",
                        ["Ahmedabad City", "Daskroi", "Dholka", "Sanand", "Viramgam"],
                    ),
                ],
            ),
            (
                "Karnataka",
                "KA",
                "South",
                [
                    (
                        "Bangalore",
                        "BLR",
                        [
                            "Bangalore North",
                            "Bangalore South",
                            "Bangalore East",
                            "Anekal",
                            "Devanahalli",
                        ],
                    ),
                ],
            ),
            (
                "Rajasthan",
                "RJ",
                "West",
                [
                    ("Jaipur", "JAI", ["Jaipur", "Sanganer", "Amber", "Shahpura", "Chomu"]),
                ],
            ),
            (
                "Andhra Pradesh",
                "AP",
                "South",
                [
                    (
                        "Visakhapatnam",
                        "VSK",
                        ["Visakhapatnam", "Gajuwaka", "Anakapalle", "Paderu", "Bheemunipatnam"],
                    ),
                ],
            ),
            (
                "Telangana",
                "TS",
                "South",
                [
                    (
                        "Hyderabad",
                        "HYD",
                        ["Hyderabad", "Secunderabad", "Rangareddy", "Medchal", "Sangareddy"],
                    ),
                ],
            ),
            (
                "Bihar",
                "BR",
                "East",
                [
                    ("Patna", "PTA", ["Patna", "Danapur", "Phulwari", "Khagaul", "Bikram"]),
                ],
            ),
        ]

        states = {}
        all_districts = []
        all_villages = []
        for s_name, s_code, s_region, districts in states_data:
            state = State(name=s_name, code=s_code, region=s_region)
            db.add(state)
            await db.flush()
            states[s_code] = state
            for d_name, d_code, villages in districts:
                district = District(state_id=state.id, name=d_name, code=d_code)
                db.add(district)
                await db.flush()
                all_districts.append(district)
                for v_name in villages:
                    village = Village(
                        district_id=district.id,
                        tehsil=v_name,
                        name=f"{v_name} Village",
                        code=f"{d_code}-{v_name[:3].upper()}",
                    )
                    db.add(village)
                    all_villages.append(village)
        print(
            f"  ✅ {len(states)} states, {len(all_districts)} districts, {len(all_villages)} villages"
        )

        # ===== MINISTRIES =====
        ministries_data = [
            ("Ministry of Road Transport & Highways", "MoRTH"),
            ("Ministry of Railways", "MoR"),
            ("Ministry of Jal Shakti", "MoJS"),
            ("Ministry of Commerce & Industry", "MoCI"),
            ("Ministry of New & Renewable Energy", "MNRE"),
        ]
        ministries = []
        for name, code in ministries_data:
            m = Ministry(name=name, code=code)
            db.add(m)
            ministries.append(m)
        await db.flush()
        print(f"  ✅ {len(ministries)} ministries")

        # ===== CATEGORIES =====
        categories_data = [
            "Highway",
            "Railway",
            "Irrigation",
            "Industrial Corridor",
            "Renewable Energy",
            "Smart City",
            "Airport",
            "Defence",
            "Welfare",
        ]
        categories = []
        for name in categories_data:
            c = ProjectCategory(name=name)
            db.add(c)
            categories.append(c)
        await db.flush()
        print(f"  ✅ {len(categories)} categories")

        # ===== USERS (40+) =====
        password_hash = get_password_hash("password123")
        users = []
        user_specs = [
            # super_admin
            ("Rajesh Kumar", "rajesh@nlams.gov.in", "9876543210", "super_admin", None, None, None),
            ("Priya Sharma", "priya@nlams.gov.in", "9876543211", "super_admin", None, None, None),
            # state_authority
            (
                "Anil Deshmukh",
                "anil@maharashtra.gov.in",
                "9876543212",
                "state_authority",
                states["MH"],
                None,
                None,
            ),
            (
                "Sunita Verma",
                "sunita@mp.gov.in",
                "9876543213",
                "state_authority",
                states["MP"],
                None,
                None,
            ),
            (
                "Karthik Iyer",
                "karthik@tn.gov.in",
                "9876543214",
                "state_authority",
                states["TN"],
                None,
                None,
            ),
            (
                "Amit Singh",
                "amit@up.gov.in",
                "9876543215",
                "state_authority",
                states["UP"],
                None,
                None,
            ),
            # district_officer
            (
                "Suresh Patil",
                "suresh@nagpur.gov.in",
                "9876543216",
                "district_officer",
                states["MH"],
                all_districts[0],
                None,
            ),
            (
                "Meena Yadav",
                "meena@bhopal.gov.in",
                "9876543217",
                "district_officer",
                states["MP"],
                all_districts[3],
                None,
            ),
            (
                "Vikram Reddy",
                "vikram@chennai.gov.in",
                "9876543218",
                "district_officer",
                states["TN"],
                all_districts[6],
                None,
            ),
            (
                "Deepak Joshi",
                "deepak@lucknow.gov.in",
                "9876543219",
                "district_officer",
                states["UP"],
                all_districts[9],
                None,
            ),
            (
                "Ravi Kumar",
                "ravi@indore.gov.in",
                "9876543220",
                "district_officer",
                states["MP"],
                all_districts[4],
                None,
            ),
            # agency
            (
                "NHAI Project Office",
                "agency@nhai.gov.in",
                "9876543221",
                "agency",
                states["MH"],
                None,
                "National Highways Authority of India",
            ),
            (
                "IRCON International",
                "agency@ircon.co.in",
                "9876543222",
                "agency",
                states["MP"],
                None,
                "IRCON International Ltd",
            ),
            (
                "L&T Infrastructure",
                "agency@ltinfra.com",
                "9876543223",
                "agency",
                states["TN"],
                None,
                "Larsen & Toubro Infrastructure",
            ),
            (
                "NBCC India",
                "agency@nbcc.co.in",
                "9876543224",
                "agency",
                states["UP"],
                None,
                "National Buildings Construction Corp",
            ),
            (
                "Adani Green",
                "agency@adanigreen.com",
                "9876543225",
                "agency",
                states["GJ"],
                None,
                "Adani Green Energy Ltd",
            ),
            # field_officer
            (
                "Rahul Deshpande",
                "rahul.f@nlams.gov.in",
                "9876543226",
                "field_officer",
                states["MH"],
                all_districts[0],
                None,
            ),
            (
                "Sanjay Kulkarni",
                "sanjay.f@nlams.gov.in",
                "9876543227",
                "field_officer",
                states["MH"],
                all_districts[1],
                None,
            ),
            (
                "Prakash Tiwari",
                "prakash.f@nlams.gov.in",
                "9876543228",
                "field_officer",
                states["MP"],
                all_districts[3],
                None,
            ),
            (
                "Arun Nair",
                "arun.f@nlams.gov.in",
                "9876543229",
                "field_officer",
                states["TN"],
                all_districts[6],
                None,
            ),
            (
                "Manoj Singh",
                "manoj.f@nlams.gov.in",
                "9876543230",
                "field_officer",
                states["UP"],
                all_districts[9],
                None,
            ),
            (
                "Ajay Meena",
                "ajay.f@nlams.gov.in",
                "9876543231",
                "field_officer",
                states["MP"],
                all_districts[4],
                None,
            ),
            # citizens
            (
                "Ganesh Waghmare",
                "ganesh@email.com",
                "9876543232",
                "citizen",
                states["MH"],
                all_districts[0],
                None,
            ),
            (
                "Lata Bhosale",
                "lata@email.com",
                "9876543233",
                "citizen",
                states["MH"],
                all_districts[0],
                None,
            ),
            (
                "Ram Prasad",
                "ram@email.com",
                "9876543234",
                "citizen",
                states["MP"],
                all_districts[3],
                None,
            ),
            (
                "Sita Devi",
                "sita@email.com",
                "9876543235",
                "citizen",
                states["MP"],
                all_districts[3],
                None,
            ),
            (
                "Kumar Rajan",
                "kumar@email.com",
                "9876543236",
                "citizen",
                states["TN"],
                all_districts[6],
                None,
            ),
            (
                "Aarti Patel",
                "aarti@email.com",
                "9876543237",
                "citizen",
                states["GJ"],
                all_districts[12],
                None,
            ),
            (
                "Babu Lal",
                "babu@email.com",
                "9876543238",
                "citizen",
                states["UP"],
                all_districts[9],
                None,
            ),
            (
                "Champa Bai",
                "champa@email.com",
                "9876543239",
                "citizen",
                states["UP"],
                all_districts[9],
                None,
            ),
        ]

        for full_name, email, phone, role_name, state, district, agency in user_specs:
            u = User(
                full_name=full_name,
                email=email,
                phone=phone,
                password_hash=password_hash,
                role_id=roles[role_name].id,
                state_id=state.id if state else None,
                district_id=district.id if district else None,
                agency_name=agency,
            )
            db.add(u)
            users.append(u)
        await db.flush()
        print(f"  ✅ {len(users)} users created")

        # ===== PROJECTS (15 realistic) =====
        projects_data = [
            (
                "NH-44 Widening — Nagpur to Betul",
                ministries[0],
                categories[0],
                users[11],
                states["MH"],
                all_districts[0],
                2500000000,
                120.5,
                "high",
                "active",
                "compensation_assessment",
            ),
            (
                "Bhogapuram International Airport Land Pooling",
                ministries[3],
                categories[6],
                users[13],
                states["AP"],
                all_districts[15],
                8000000000,
                500.0,
                "critical",
                "active",
                "district_verification",
            ),
            (
                "Delhi-Mumbai Industrial Corridor — Phase II",
                ministries[3],
                categories[3],
                users[14],
                states["MH"],
                all_districts[1],
                15000000000,
                2000.0,
                "critical",
                "approved",
                "gis_mapping",
            ),
            (
                "Narmada River Irrigation Project — Betul",
                ministries[2],
                categories[2],
                users[12],
                states["MP"],
                all_districts[5],
                1200000000,
                800.0,
                "high",
                "active",
                "legal_notification",
            ),
            (
                "Chennai Metro Phase III Extension",
                ministries[0],
                categories[5],
                users[13],
                states["TN"],
                all_districts[6],
                5000000000,
                150.0,
                "high",
                "under_review",
                "dpr_upload",
            ),
            (
                "Lucknow–Varanasi Expressway",
                ministries[0],
                categories[0],
                users[14],
                states["UP"],
                all_districts[9],
                3500000000,
                350.0,
                "high",
                "active",
                "objection_handling",
            ),
            (
                "Bhopal Smart City — Phase II",
                ministries[3],
                categories[5],
                users[12],
                states["MP"],
                all_districts[3],
                2000000000,
                50.0,
                "medium",
                "approved",
                "compensation_assessment",
            ),
            (
                "Adani Solar Park — Rewa",
                ministries[4],
                categories[4],
                users[15],
                states["MP"],
                all_districts[3],
                4000000000,
                600.0,
                "medium",
                "active",
                "payment_disbursement",
            ),
            (
                "Pune–Nagpur Railway Line Doubling",
                ministries[1],
                categories[1],
                users[12],
                states["MH"],
                all_districts[2],
                6000000000,
                400.0,
                "high",
                "delayed",
                "award_declaration",
            ),
            (
                "Ahmedabad Metro Extension",
                ministries[0],
                categories[5],
                users[14],
                states["GJ"],
                all_districts[12],
                3000000000,
                80.0,
                "high",
                "active",
                "physical_possession",
            ),
            (
                "Varanasi Heritage Corridor Project",
                ministries[3],
                categories[5],
                users[14],
                states["UP"],
                all_districts[10],
                1500000000,
                30.0,
                "critical",
                "active",
                "rehabilitation_resettlement",
            ),
            (
                "Hyderabad Defence Corridor",
                ministries[3],
                categories[7],
                users[14],
                states["TS"],
                all_districts[14],
                7000000000,
                300.0,
                "critical",
                "approved",
                "state_review",
            ),
            (
                "Jaipur Ring Road Project",
                ministries[0],
                categories[0],
                users[14],
                states["RJ"],
                all_districts[13],
                2200000000,
                180.0,
                "medium",
                "completed",
                "project_completion",
            ),
            (
                "Coimbatore Water Supply Project",
                ministries[2],
                categories[2],
                users[13],
                states["TN"],
                all_districts[7],
                800000000,
                40.0,
                "medium",
                "draft",
                "project_proposal",
            ),
            (
                "Patna–Gaya Railway Overhaul",
                ministries[1],
                categories[1],
                users[14],
                states["BR"],
                all_districts[15],
                4500000000,
                250.0,
                "high",
                "active",
                "compensation_assessment",
            ),
        ]

        projects = []
        for i, (
            name,
            ministry,
            cat,
            agency_user,
            state,
            district,
            budget,
            land_ha,
            priority,
            status,
            stage,
        ) in enumerate(projects_data):
            p = Project(
                name=name,
                ministry_id=ministry.id,
                category_id=cat.id,
                implementing_agency_id=agency_user.id,
                state_id=state.id,
                district_id=district.id,
                description=f"National infrastructure project: {name}. Strategic importance for regional development.",
                estimated_budget=budget,
                estimated_land_required_hectares=land_ha,
                priority=priority,
                current_stage=stage,
                status=status,
                created_by=users[0].id,
                start_date=datetime.now(timezone.utc) - timedelta(days=random.randint(30, 365)),
                target_completion_date=datetime.now(timezone.utc)
                + timedelta(days=random.randint(180, 1095)),
            )
            db.add(p)
            projects.append(p)
        await db.flush()
        print(f"  ✅ {len(projects)} projects created")

        # ===== MILESTONES for first 5 projects (with full timeline) =====
        stage_labels = {
            "project_proposal": "Project Proposal Submitted",
            "dpr_upload": "DPR Document Uploaded",
            "land_requirement": "Land Requirement Assessment",
            "state_review": "State-Level Review Completed",
            "district_verification": "District Verification Done",
            "gis_mapping": "GIS Parcel Mapping Completed",
            "legal_notification": "Legal Notification Issued (Section 11/19)",
            "objection_handling": "Objection Hearing & Resolution",
            "compensation_assessment": "Compensation Assessment Done",
            "award_declaration": "Award Declaration Published",
            "payment_disbursement": "Payment Disbursement Completed",
            "physical_possession": "Physical Possession Taken",
            "rehabilitation_resettlement": "R&R Program Completed",
            "project_completion": "Project Marked Complete",
        }

        for proj in projects[:5]:
            stage_index = STAGES.index(proj.current_stage) if proj.current_stage in STAGES else 0
            for idx, stage in enumerate(STAGES):
                is_completed = idx < stage_index
                is_current = idx == stage_index
                ms = Milestone(
                    project_id=proj.id,
                    stage=stage,
                    title=stage_labels.get(stage, stage.replace("_", " ").title()),
                    planned_date=proj.start_date + timedelta(days=30 * (idx + 1))
                    if proj.start_date
                    else None,
                    actual_date=(
                        proj.start_date + timedelta(days=30 * (idx + 1) + random.randint(-5, 15))
                    )
                    if is_completed and proj.start_date
                    else None,
                    status=MilestoneStatus.completed
                    if is_completed
                    else (MilestoneStatus.in_progress if is_current else MilestoneStatus.pending),
                    responsible_officer_id=random.choice(users[:10]).id,
                    remarks="Completed successfully"
                    if is_completed
                    else ("In progress — monitoring" if is_current else None),
                )
                db.add(ms)
        await db.flush()
        print("  ✅ Milestones created for flagship projects")

        # ===== LAND PARCELS (60+) =====
        parcels = []
        parcel_index = 0
        for proj in projects:
            num_parcels = random.randint(3, 8)
            for j in range(num_parcels):
                village = random.choice(all_villages)
                district_obj = await db.get(District, village.district_id)
                state_obj = await db.get(District, district_obj.state_id) if district_obj else None
                state_id = district_obj.state_id if district_obj else projects_data[0][4].id

                # Generate real-ish polygon coordinates around Nagpur/MP region
                base_lat = 21.1458 + random.uniform(-2, 2)
                base_lng = 79.0882 + random.uniform(-2, 2)
                area = round(random.uniform(0.5, 25.0), 4)
                size = 0.01 * (area**0.5)

                polygon = {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [base_lng, base_lat],
                            [base_lng + size, base_lat],
                            [base_lng + size, base_lat + size],
                            [base_lng, base_lat + size],
                            [base_lng, base_lat],
                        ]
                    ],
                }

                land_type = random.choice(list(LandType))
                ownership = random.choice(list(OwnershipStatus))
                v_status = random.choice(list(VerificationStatus))

                parcel = LandParcel(
                    project_id=proj.id,
                    survey_number=f"SV-{proj.name[:3].upper()}-{j + 1:03d}",
                    village_id=village.id,
                    district_id=district_obj.id if district_obj else all_districts[0].id,
                    state_id=state_id,
                    area_hectares=area,
                    geom=str(polygon),
                    land_type=land_type,
                    ownership_status=ownership,
                    verification_status=v_status,
                )
                db.add(parcel)
                parcels.append(parcel)
                parcel_index += 1
        await db.flush()
        print(f"  ✅ {len(parcels)} land parcels created")

        # ===== LAND OWNERS =====
        owner_names = [
            ("Ganesh Waghmare", "9876543232"),
            ("Lata Bhosale", "9876543233"),
            ("Ram Prasad", "9876543234"),
            ("Sita Devi", "9876543235"),
            ("Kumar Rajan", "9876543236"),
            ("Aarti Patel", "9876543237"),
            ("Babu Lal", "9876543238"),
            ("Champa Bai", "9876543239"),
            ("Dattatraya Mahajan", "9876543240"),
            ("Savitribai Phule", "9876543241"),
            ("Tukaram Bholu", "9876543242"),
            ("Narayanrao Raut", "9876543243"),
        ]
        owners = []
        for parcel in parcels[:40]:
            owner_name, owner_phone = random.choice(owner_names)
            owner = LandOwner(
                parcel_id=parcel.id,
                full_name=owner_name,
                aadhaar_masked=f"XXXX-XXXX-{random.randint(1000, 9999)}",
                phone=owner_phone,
                bank_account_masked=f"XXXX-XXXX-{random.randint(1000, 9999)}",
                ifsc=random.choice(["SBIN0001234", "HDFC0004567", "ICIC0007890", "PUNB0001111"]),
                share_percentage=random.choice([100, 60, 40, 50, 30, 70]),
            )
            db.add(owner)
            owners.append(owner)
        await db.flush()
        print(f"  ✅ {len(owners)} land owners created")

        # ===== COMPENSATION for first 5 projects =====
        compensations = []
        for proj in projects[:5]:
            proj_parcels = [p for p in parcels if p.project_id == proj.id]
            for parcel in proj_parcels[:3]:
                market_value = float(parcel.area_hectares or 1) * random.uniform(300000, 2000000)
                solatium = market_value * 1.0  # 100% per LARR Act
                additional = market_value * random.uniform(0, 0.3)
                comp = Compensation(
                    parcel_id=parcel.id,
                    market_value=round(market_value, 2),
                    solatium=round(solatium, 2),
                    additional_compensation=round(additional, 2),
                    total_award=round(market_value + solatium + additional, 2),
                    assessed_by=users[6].id,
                    assessment_date=datetime.now(timezone.utc)
                    - timedelta(days=random.randint(10, 60)),
                    status=random.choice(["assessed", "approved"]),
                )
                db.add(comp)
                compensations.append(comp)
        await db.flush()
        print(f"  ✅ {len(compensations)} compensation records")

        # ===== PAYMENTS =====
        payments = []
        for comp in compensations:
            parcel_owners = [o for o in owners if o.parcel_id == comp.parcel_id]
            for owner in parcel_owners[:1]:
                payment = Payment(
                    compensation_id=comp.id,
                    land_owner_id=owner.id,
                    amount=float(comp.total_award or 0)
                    * (float(owner.share_percentage or 100) / 100),
                    pfms_reference=f"PFMS-{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=12))}",
                    bank_verification_status=random.choice(["pending", "verified", "verified"]),
                    payment_status=random.choice(
                        ["pending", "processing", "disbursed", "disbursed"]
                    ),
                    disbursed_date=datetime.now(timezone.utc)
                    - timedelta(days=random.randint(0, 30))
                    if random.random() > 0.5
                    else None,
                )
                db.add(payment)
                payments.append(payment)
        await db.flush()
        print(f"  ✅ {len(payments)} payments")

        # ===== POSSESSION =====
        for comp in compensations[:5]:
            pos = Possession(
                parcel_id=comp.parcel_id,
                possession_date=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 20)),
                taken_by=users[6].id,
                possession_type="physical",
                remarks="Physical possession taken after full compensation disbursement",
            )
            db.add(pos)
        await db.flush()
        print("  ✅ Possession records created")

        # ===== R&R FAMILIES =====
        rr_families = []
        for proj in projects[:5]:
            for k in range(random.randint(3, 8)):
                fam = RehabilitationFamily(
                    project_id=proj.id,
                    family_head_name=random.choice([o[0] for o in owner_names]),
                    family_id_number=f"RR-{proj.name[:3].upper()}-{k + 1:03d}",
                    member_count=random.randint(3, 8),
                    displaced_status=random.choice(["fully", "partially", "not_displaced"]),
                    housing_benefit_status=random.choice(
                        ["provided", "in_progress", "not_started"]
                    ),
                    employment_benefit_status=random.choice(
                        ["provided", "in_progress", "not_started"]
                    ),
                    monetary_benefit_amount=round(random.uniform(50000, 500000), 2),
                    current_stage=random.choice(
                        ["identification", "verification", "benefit_disbursement", "resettled"]
                    ),
                    progress_percentage=random.randint(0, 100),
                )
                db.add(fam)
                rr_families.append(fam)
        await db.flush()
        print(f"  ✅ {len(rr_families)} R&R families")

        # ===== LEGAL NOTIFICATIONS =====
        for proj in projects[:5]:
            ln = LegalNotification(
                project_id=proj.id,
                section_type=random.choice(["Section 11", "Section 19"]),
                notification_number=f"LN-{proj.name[:3].upper()}-001",
                issued_date=datetime.now(timezone.utc) - timedelta(days=random.randint(20, 90)),
                status="issued",
            )
            db.add(ln)
        await db.flush()
        print("  ✅ Legal notifications created")

        # ===== CIRCLE RATES =====
        for state_code, state_obj in states.items():
            for district in [d for d in all_districts if d.state_id == state_obj.id]:
                for lt in ["agricultural", "residential", "commercial"]:
                    base_rates = {
                        "agricultural": 500000,
                        "residential": 2000000,
                        "commercial": 5000000,
                    }
                    cr = CircleRate(
                        state_id=state_obj.id,
                        district_id=district.id,
                        land_type=lt,
                        rate_per_hectare=base_rates[lt] * random.uniform(0.7, 1.5),
                        financial_year="2024-25",
                    )
                    db.add(cr)
        await db.flush()
        print("  ✅ Circle rates seeded")

        # ===== AUDIT LOGS for flagship project =====
        flagship = projects[0]
        for idx, stage in enumerate(STAGES[:8]):
            audit = AuditLog(
                entity_type="project",
                entity_id=flagship.id,
                action="stage_change",
                performed_by=random.choice(users[:10]).id,
                old_value={"stage": STAGES[idx - 1] if idx > 0 else None},
                new_value={"stage": stage},
                remarks=f"Project advanced to {stage_labels.get(stage, stage)}",
                ip_address="10.0.0.1",
            )
            db.add(audit)
        await db.flush()
        print("  ✅ Audit trail created for flagship project")

        # ===== NOTIFICATIONS =====
        for user in users:
            for _ in range(random.randint(1, 4)):
                notif = NotificationApp(
                    user_id=user.id,
                    title=random.choice(
                        [
                            "Project status updated",
                            "New compensation assessment ready",
                            "Document uploaded for review",
                            "Payment processed successfully",
                            "GIS mapping completed for parcel",
                            "Objection hearing scheduled",
                        ]
                    ),
                    body="Your action may be required. Please review the latest updates.",
                    type=random.choice(["info", "success", "warning"]),
                    channel="in_app",
                    is_read=random.choice([True, False]),
                )
                db.add(notif)
        await db.flush()
        print("  ✅ In-app notifications created")

        # ===== DOCUMENTS =====
        for proj in projects[:5]:
            for doc_type in ["dpr", "notification", "award"]:
                doc = Document(
                    project_id=proj.id,
                    uploaded_by=users[0].id,
                    doc_type=doc_type,
                    file_name=f"{doc_type}_{proj.name[:20].replace(' ', '_')}.pdf",
                    file_path=f"documents/{doc_type}_{proj.id}.pdf",
                    file_size=random.randint(50000, 5000000),
                    mime_type="application/pdf",
                )
                db.add(doc)
        await db.flush()
        print("  ✅ Sample documents created")

        await db.commit()
        print("\n🎉 Database seeded successfully!")
        print("\n📋 Default Login Credentials:")
        print("=" * 60)
        print(f"{'Role':<20} {'Email':<35} {'Password':<15}")
        print("=" * 60)
        creds = [
            ("Super Admin", "rajesh@nlams.gov.in"),
            ("State Auth", "anil@maharashtra.gov.in"),
            ("District Officer", "suresh@nagpur.gov.in"),
            ("Agency", "agency@nhai.gov.in"),
            ("Field Officer", "rahul.f@nlams.gov.in"),
            ("Citizen", "ganesh@email.com"),
        ]
        for role, email in creds:
            print(f"{role:<20} {email:<35} {'password123':<15}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed())
