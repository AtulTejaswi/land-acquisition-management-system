"""Seed script for NLAMS - National Land Acquisition & Management System

Creates realistic Indian data for the 48-hour SIH demo:
- 5 ministries
- 10 states with real districts/villages
- 40+ users across all 6 roles
- 15 realistic projects at various stages
- 60+ land parcels with approximate real-world coordinates
- compensation + payment + R&R records for 5 fully-progressed projects
- audit trail history for one flagship project
"""

import os
import uuid
import random
import json
from datetime import datetime, timedelta, date
from decimal import Decimal

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import engine

from app.models.state import State, District, Village
from app.models.user import User, Role
from app.models.project import Project, ProjectCategory, Ministry, Milestone, ProjectStatus, MilestoneStatus, STAGES
from app.models.land import LandParcel, LandOwner, SurveyRecord, LandType, OwnershipStatus, VerificationStatus
from app.models.legal import LegalNotification, Objection, NotificationLegalStatus, ObjectionStatus
from app.models.compensation import Compensation, Payment, CompensationStatus, BankVerificationStatus, PaymentStatus
from app.models.possession import Possession, PossessionType
from app.models.rr import RehabilitationFamily, DisplacedStatus, BenefitStatus, RRStage
from app.models.document import Document, DocType
from app.models.audit import AuditLog
from app.models.notification import NotificationApp, NotificationType, NotificationChannel
from app.models.circle_rate import CircleRate


def random_date(start: date, end: date) -> datetime:
    return datetime(
        year=random.randint(start.year, end.year),
        month=random.randint(start.month, end.month),
        day=random.randint(1, 28),
        hour=random.randint(0, 23),
        minute=random.randint(0, 59),
        second=random.randint(0, 59),
    )


def rand(min_val: int, max_val: int) -> int:
    return random.randint(min_val, max_val)


INDIAN_STATES = {
    "Maharashtra": "MH",
    "Gujarat": "GJ",
    "Rajasthan": "RJ",
    "Madhya Pradesh": "MP",
    "Uttar Pradesh": "UP",
    "Karnataka": "KA",
    "Tamil Nadu": "TN",
    "Andhra Pradesh": "AP",
    "Telangana": "TS",
    "West Bengal": "WB",
}

INDIAN_DISTRICTS = {
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Kota", "Udaipur"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Agra", "Varanasi"],
    "Karnataka": ["Bangalore", "Mysore", "Hubli", "Mangalore"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Trichy"],
    "Andhra Pradesh": ["Amaravati", "Vijayawada", "Visakhapatnam"],
    "Telangana": ["Hyderabad", "Warangal", "Karimnagar"],
    "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Siliguri"],
}

INDIAN_VILLAGES = {
    "Mumbai": ["Mumbai Central", "Dharavi", "Andheri", "Bandra"],
    "Pune": ["Pune City", "Pimpri", "Pashan", "Kharadi"],
    "Nagpur": ["Nagpur City", "Kamptee", "Butibori", "Nandanwan"],
    "Nashik": ["Nashik City", "Sinnar", "Nandgaon", "Igatpuri"],
    "Ahmedabad": ["Ahmedabad City", "Ghodiad", "Bodakdev", "Satellite"],
    "Surat": ["Surat City", "Mugappura", "Udhana", "Variav"],
    "Jaipur": ["Jaipur City", "Malpura", "Phagi", "Chaksu"],
    "Jodhpur": ["Jodhpur City", "Bilara", "Osian", "Phalodi"],
    "Bhopal": ["Bhopal City", "Piparia", "Berasia", "Kurwa"],
    "Indore": ["Indore City", "Depalpur", "Mhow", "Sanwer"],
}


def seed_database():
    print("Starting database seeding...")
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # === ROLES ===
        print("Seeding roles...")
        roles_data = [
            {"name": "super_admin", "description": "Central Ministry super administrator"},
            {"name": "state_authority", "description": "State-level land acquisition authority"},
            {"name": "district_officer", "description": "District Collector/LAO officer"},
            {"name": "agency", "description": "Project implementing agency representative"},
            {"name": "field_officer", "description": "Field officer (mobile-first)"},
            {"name": "citizen", "description": "Citizen / land owner"},
        ]
        roles = {}
        for r in roles_data:
            role = Role(name=r["name"], description=r["description"])
            db.add(role)
            db.flush()
            roles[r["name"]] = role

        # === MINISTRIES ===
        print("Seeding ministries...")
        ministries_data = [
            {"name": "Ministry of Road Transport and Highways", "code": "MoRTH"},
            {"name": "Ministry of Rural Development", "code": "MRD"},
            {"name": "Ministry of Railways", "code": "MoR"},
            {"name": "Ministry of Power", "code": "MoP"},
            {"name": "Ministry of Jal Shakti", "code": "MJS"},
        ]
        ministries = []
        for m in ministries_data:
            ministry = Ministry(name=m["name"], code=m["code"])
            db.add(ministry)
            ministries.append(ministry)
        db.flush()

        # === PROJECT CATEGORIES ===
        print("Seeding project categories...")
        categories_data = ["Highway", "Railway", "Irrigation", "Industrial Corridor", "Renewable Energy", "Smart City", "Airport", "Defence"]
        categories = []
        for c in categories_data:
            category = ProjectCategory(name=c)
            db.add(category)
            categories.append(category)
        db.flush()

        # === STATES, DISTRICTS, VILLAGES ===
        print("Seeding states, districts, villages...")
        state_objects = []
        district_objects = {}
        village_objects = {}
        for state_name, state_code in INDIAN_STATES.items():
            state = State(name=state_name, code=state_code)
            db.add(state)
            db.flush()
            state_objects.append(state)

            districts_list = INDIAN_DISTRICTS.get(state_name, [])
            for i, dist_name in enumerate(districts_list[:2], 1):
                district = District(name=dist_name, state_id=state.id, code=f"{state_code}{i:02d}")
                db.add(district)
                db.flush()
                district_objects[f"{state_name}_{dist_name}"] = district

                villages_list = INDIAN_VILLAGES.get(dist_name, [f"Village{i}"])
                for j, village_name in enumerate(villages_list[:2], 1):
                    village = Village(name=village_name, district_id=district.id, tehsil=f"{dist_name} Tehsil", code=f"{state_code}{i:02d}{j:02d}")
                    db.add(village)
                    db.flush()
                    village_objects[f"{dist_name}_{village_name}"] = village

        print(f"  Created {len(state_objects)} states with districts and villages")

        # === USERS ===
        print("Seeding users...")
        password_hash = get_password_hash("password123")
        all_users = []

        # Super Admin
        sa = User(full_name="Rajesh Sharma", email="rajesh@nlams.gov.in", phone="+91-98100-00001",
                  password_hash=password_hash, role_id=roles["super_admin"].id, state_id=state_objects[0].id, is_active=True)
        db.add(sa); db.flush(); all_users.append(sa)

        # State Authority
        state_auth_users = []
        for i, (state, count) in enumerate([(state_objects[0], 2), (state_objects[1], 2)]):
            for j in range(count):
                u = User(full_name=f"State Officer {i*2+j+1}", email=f"state{i*2+j+1}@nlams.gov.in",
                         phone=f"+91-98100-00{j+2:02d}", password_hash=password_hash,
                         role_id=roles["state_authority"].id, state_id=state.id, is_active=True)
                db.add(u); db.flush(); state_auth_users.append(u); all_users.append(u)

        # District Officers
        district_users = []
        for i, state in enumerate(state_objects[:4]):
            for j in range(2):
                dist = district_objects.get(f"{state.name}_{INDIAN_DISTRICTS[state.name][0]}")
                if dist:
                    u = User(full_name=f"District Officer {i*2+j+1}", email=f"district{i*2+j+1}@nlams.gov.in",
                             phone=f"+91-98100-0{j+11:02d}", password_hash=password_hash,
                             role_id=roles["district_officer"].id, state_id=state.id, district_id=dist.id, is_active=True)
                    db.add(u); db.flush(); district_users.append(u); all_users.append(u)

        # Agency
        agency_users = []
        for i in range(4):
            u = User(full_name=f"Agency Rep {i+1}", email=f"agency{i+1}@nhai.gov.in",
                     phone=f"+91-98100-000{i+5}", password_hash=password_hash,
                     role_id=roles["agency"].id, state_id=state_objects[i % len(state_objects)].id,
                     agency_name=f"NHAI Division {i+1}", is_active=True)
            db.add(u); db.flush(); agency_users.append(u); all_users.append(u)

        # Field Officers
        field_users = []
        for i in range(6):
            fo_state = state_objects[i % len(state_objects)]
            u = User(full_name=f"Field Officer {i+1}", email=f"field{i+1}@nlams.gov.in",
                     phone=f"+91-98100-000{i+9}", password_hash=password_hash,
                     role_id=roles["field_officer"].id, state_id=fo_state.id, is_active=True)
            db.add(u); db.flush(); field_users.append(u); all_users.append(u)

        # Citizens
        citizen_users = []
        for i in range(8):
            u = User(full_name=f"Land Owner {i+1}", email=f"citizen{i+1}@email.com",
                     phone=f"+91-98100-00{i+20:02d}", password_hash=password_hash,
                     role_id=roles["citizen"].id, is_active=True)
            db.add(u); db.flush(); citizen_users.append(u); all_users.append(u)

        print(f"  Created {len(all_users)} users")

        # === CIRCLE RATES ===
        print("Seeding circle rates...")
        for state in state_objects:
            for land_type in ["agricultural", "residential", "commercial"]:
                cr = CircleRate(state_id=state.id, district_id=None, land_type=land_type,
                                rate_per_hectare=Decimal(str(rand(10000, 500000))),
                                financial_year="2024-25")
                db.add(cr)

        # === PROJECTS ===
        print("Seeding projects...")
        p1 = Project(name="NH-44 Widening — Nagpur to Betul", ministry_id=ministries[0].id, category_id=categories[0].id,
                     implementing_agency_id=agency_users[0].id, state_id=state_objects[0].id,
                     district_id=district_objects["Maharashtra_Nagpur"].id,
                     description="Widening of NH-44 from Nagpur to Betul section, 280 km corridor",
                     estimated_budget=Decimal("18500000000.00"), estimated_land_required_hectares=Decimal("1250.000"),
                     priority="high", current_stage="physical_possession", status="completed",
                     start_date=datetime(2022, 3, 15), target_completion_date=datetime(2024, 12, 31), created_by=sa.id)
        db.add(p1)

        p2 = Project(name="Bhogapuram International Airport Land Pooling", ministry_id=ministries[0].id, category_id=categories[6].id,
                     implementing_agency_id=agency_users[1].id, state_id=state_objects[7].id,
                     district_id=district_objects.get("Andhra Pradesh_Vijayawada", district_objects["Andhra Pradesh_Amaravati"]).id,
                     description="Land pooling for Bhogapuram International Airport development",
                     estimated_budget=Decimal("52000000000.00"), estimated_land_required_hectares=Decimal("3500.000"),
                     priority="critical", current_stage="compensation_assessment", status="approved",
                     start_date=datetime(2021, 6, 1), target_completion_date=datetime(2026, 3, 31), created_by=agency_users[1].id)
        db.add(p2)

        p3 = Project(name="North-South Freight Corridor - Phase 2", ministry_id=ministries[2].id, category_id=categories[1].id,
                     implementing_agency_id=agency_users[2].id, state_id=state_objects[3].id,
                     district_id=district_objects["Madhya Pradesh_Bhopal"].id,
                     description="Freight corridor development for enhanced rail connectivity",
                     estimated_budget=Decimal("38000000000.00"), estimated_land_required_hectares=Decimal("2100.000"),
                     priority="high", current_stage="gis_mapping", status="under_review",
                     start_date=datetime(2022, 1, 10), target_completion_date=datetime(2025, 9, 30), created_by=agency_users[2].id)
        db.add(p3)

        p4 = Project(name="Solar Power Park - Jodhpur Region", ministry_id=ministries[3].id, category_id=categories[4].id,
                     implementing_agency_id=agency_users[3].id, state_id=state_objects[2].id,
                     district_id=district_objects["Rajasthan_Jodhpur"].id,
                     description="Large-scale solar power generation facility",
                     estimated_budget=Decimal("8500000000.00"), estimated_land_required_hectares=Decimal("500.000"),
                     priority="medium", current_stage="land_requirement", status="submitted",
                     start_date=datetime(2023, 8, 1), target_completion_date=datetime(2025, 3, 31), created_by=agency_users[3].id)
        db.add(p4)

        p5 = Project(name="Waghur Irrigation Project - Maharashtra", ministry_id=ministries[1].id, category_id=categories[2].id,
                     implementing_agency_id=agency_users[0].id, state_id=state_objects[0].id,
                     district_id=district_objects["Maharashtra_Nagpur"].id,
                     description="Irrigation project on Waghur river for agricultural development",
                     estimated_budget=Decimal("12000000000.00"), estimated_land_required_hectares=Decimal("800.000"),
                     priority="high", current_stage="payment_disbursement", status="delayed",
                     start_date=datetime(2020, 6, 1), target_completion_date=datetime(2024, 6, 30), created_by=sa.id)
        db.add(p5)

        p6 = Project(name="Kosi Bridge Construction", ministry_id=ministries[0].id, category_id=categories[0].id,
                     implementing_agency_id=agency_users[1].id, state_id=state_objects[4].id,
                     district_id=district_objects["Uttar Pradesh_Lucknow"].id,
                     description="Bridge construction over Kosi river for improved connectivity",
                     estimated_budget=Decimal("4500000000.00"), estimated_land_required_hectares=Decimal("250.000"),
                     priority="medium", current_stage="legal_notification", status="under_review",
                     start_date=datetime(2022, 7, 1), target_completion_date=datetime(2025, 3, 31), created_by=agency_users[1].id)
        db.add(p6)

        p7 = Project(name="Technology Investment Region - Hyderabad", ministry_id=ministries[4].id, category_id=categories[5].id,
                     implementing_agency_id=agency_users[2].id, state_id=state_objects[8].id,
                     district_id=district_objects["Telangana_Hyderabad"].id,
                     description="Tech city development with integrated infrastructure",
                     estimated_budget=Decimal("25000000000.00"), estimated_land_required_hectares=Decimal("600.000"),
                     priority="critical", current_stage="project_proposal", status="draft",
                     start_date=datetime(2024, 1, 1), target_completion_date=datetime(2028, 12, 31), created_by=sa.id)
        db.add(p7)

        p8 = Project(name="Mumbai Coastal Road - Phase 3", ministry_id=ministries[0].id, category_id=categories[0].id,
                     implementing_agency_id=agency_users[0].id, state_id=state_objects[0].id,
                     district_id=district_objects["Maharashtra_Mumbai"].id,
                     description="Coastal road development connecting western suburbs",
                     estimated_budget=Decimal("15000000000.00"), estimated_land_required_hectares=Decimal("450.000"),
                     priority="high", current_stage="dpr_upload", status="submitted",
                     start_date=datetime(2023, 2, 1), target_completion_date=datetime(2026, 6, 30), created_by=agency_users[0].id)
        db.add(p8)

        p9 = Project(name="Kanpur Metro Rail Project", ministry_id=ministries[2].id, category_id=categories[1].id,
                     implementing_agency_id=agency_users[3].id, state_id=state_objects[4].id,
                     district_id=district_objects["Uttar Pradesh_Kanpur"].id,
                     description="Metro rail construction for urban transportation",
                     estimated_budget=Decimal("11000000000.00"), estimated_land_required_hectares=Decimal("350.000"),
                     priority="high", current_stage="objection_handling", status="active",
                     start_date=datetime(2021, 11, 1), target_completion_date=datetime(2025, 3, 31), created_by=agency_users[2].id)
        db.add(p9)

        p10 = Project(name="Rishikesh Valley Irrigation & Hydroelectric", ministry_id=ministries[1].id, category_id=categories[2].id,
                      implementing_agency_id=agency_users[0].id, state_id=state_objects[4].id,
                      district_id=district_objects["Uttar Pradesh_Agra"].id,
                      description="Hydroelectric and irrigation project in valley region",
                      estimated_budget=Decimal("6800000000.00"), estimated_land_required_hectares=Decimal("450.000"),
                      priority="medium", current_stage="dpr_upload", status="submitted",
                      start_date=datetime(2023, 4, 1), target_completion_date=datetime(2026, 3, 31), created_by=agency_users[0].id)
        db.add(p10)

        p11 = Project(name="Visakhapatnam Industrial Zone Development", ministry_id=ministries[4].id, category_id=categories[3].id,
                      implementing_agency_id=agency_users[1].id, state_id=state_objects[7].id,
                      district_id=district_objects.get("Andhra Pradesh_Visakhapatnam", district_objects["Andhra Pradesh_Amaravati"]).id,
                      description="Industrial zone development with supporting infrastructure",
                      estimated_budget=Decimal("3200000000.00"), estimated_land_required_hectares=Decimal("750.000"),
                      priority="low", current_stage="gis_mapping", status="active",
                      start_date=datetime(2022, 5, 1), target_completion_date=datetime(2025, 12, 31), created_by=agency_users[1].id)
        db.add(p11)

        p12 = Project(name="Rajasthan Renewable Energy Park", ministry_id=ministries[3].id, category_id=categories[4].id,
                      implementing_agency_id=agency_users[2].id, state_id=state_objects[2].id,
                      district_id=district_objects["Rajasthan_Jaipur"].id,
                      description="Large-scale renewable energy generation facility",
                      estimated_budget=Decimal("9500000000.00"), estimated_land_required_hectares=Decimal("1200.000"),
                      priority="high", current_stage="project_completion", status="completed",
                      start_date=datetime(2019, 1, 1), target_completion_date=datetime(2024, 3, 31), created_by=sa.id)
        db.add(p12)

        p13 = Project(name="DMIC - Delhi Mumbai Industrial Corridor", ministry_id=ministries[4].id, category_id=categories[3].id,
                      implementing_agency_id=agency_users[3].id, state_id=state_objects[1].id,
                      district_id=district_objects["Gujarat_Ahmedabad"].id,
                      description="Industrial corridor development across Delhi-Mumbai region",
                      estimated_budget=Decimal("45000000000.00"), estimated_land_required_hectares=Decimal("2800.000"),
                      priority="critical", current_stage="district_verification", status="under_review",
                      start_date=datetime(2021, 8, 1), target_completion_date=datetime(2026, 9, 30), created_by=sa.id)
        db.add(p13)

        p14 = Project(name="Ganga Expressway - Phase 1", ministry_id=ministries[0].id, category_id=categories[0].id,
                      implementing_agency_id=agency_users[0].id, state_id=state_objects[3].id,
                      district_id=district_objects["Madhya Pradesh_Indore"].id,
                      description="Expressway development along Ganga river basin",
                      estimated_budget=Decimal("22000000000.00"), estimated_land_required_hectares=Decimal("1800.000"),
                      priority="critical", current_stage="physical_possession", status="active",
                      start_date=datetime(2022, 10, 1), target_completion_date=datetime(2027, 3, 31), created_by=sa.id)
        db.add(p14)

        p15 = Project(name="Bhubaneswar Smart City Initiative", ministry_id=ministries[4].id, category_id=categories[5].id,
                      implementing_agency_id=agency_users[1].id, state_id=state_objects[9].id,
                      district_id=district_objects["West Bengal_Kolkata"].id,
                      description="Smart city development with IoT infrastructure",
                      estimated_budget=Decimal("7500000000.00"), estimated_land_required_hectares=Decimal("300.000"),
                      priority="medium", current_stage="compensation_assessment", status="under_review",
                      start_date=datetime(2023, 7, 1), target_completion_date=datetime(2026, 9, 30), created_by=agency_users[0].id)
        db.add(p15)
        db.flush()

        projects = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15]
        print(f"  Created {len(projects)} projects")

        # === MILESTONES ===
        print("Seeding milestones...")
        # NH-44 (p1) - fully completed
        for i, (stage, title) in enumerate([
            ("project_proposal", "Project Proposal"), ("dpr_upload", "DPR Upload"),
            ("land_requirement", "Land Requirement"), ("state_review", "State Review"),
            ("district_verification", "District Verification"), ("gis_mapping", "GIS Mapping"),
            ("legal_notification", "Legal Notification"), ("objection_handling", "Objection Handling"),
            ("compensation_assessment", "Compensation Assessment"), ("award_declaration", "Award Declaration"),
            ("payment_disbursement", "Payment Disbursement"), ("physical_possession", "Physical Possession"),
            ("rehabilitation_resettlement", "Rehabilitation & Resettlement"), ("project_completion", "Project Completion"),
        ]):
            ms = Milestone(project_id=p1.id, stage=stage, title=title,
                          planned_date=datetime(2022, 3 + i, 1),
                          actual_date=datetime(2022, 3 + i, 28) if i < 14 else datetime(2024, 12, 31),
                          status="completed", responsible_officer_id=agency_users[0].id)
            db.add(ms)

        for proj in [p2, p3, p4, p5]:
            num_ms = rand(2, 5)
            for i in range(num_ms):
                ms = Milestone(project_id=proj.id, stage=STAGES[i], title=STAGES[i].replace("_", " ").title(),
                              planned_date=datetime(2022, 1 + i, 1),
                              status=random.choice(["completed", "in_progress", "pending"]),
                              responsible_officer_id=agency_users[0].id)
                db.add(ms)

        db.flush()
        print("  Created milestones")

        # === LAND PARCELS ===
        print("Seeding land parcels...")
        parcels = []
        for proj in projects:
            num_parcels = rand(3, 8)
            for p in range(num_parcels):
                lat = round(random.uniform(21.0, 21.5), 7)
                lng = round(random.uniform(78.0, 79.5), 7)
                survey_num = f"NH-44/{projects.index(proj)+1:03d}-{p+1:03d}"

                dist = district_objects.get(f"{proj.state.name}_{INDIAN_DISTRICTS.get(proj.state.name, [''])[0]}")
                if not dist:
                    dist = list(district_objects.values())[0]
                village = list(village_objects.values())[0] if village_objects else None

                area = round(random.uniform(0.5, 50.0), 4)
                geom = f"SRID=4326;POLYGON(({lng} {lat}, {lng+0.01} {lat}, {lng+0.01} {lat+0.01}, {lng} {lat+0.01}, {lng} {lat}))"

                parcel = LandParcel(
                    project_id=proj.id, survey_number=survey_num,
                    village_id=village.id if village else dist.id,
                    district_id=dist.id, state_id=proj.state_id,
                    area_hectares=area, geom=geom,
                    land_type=random.choice(["agricultural", "residential", "commercial", "agricultural", "other"]),
                    ownership_status=random.choice(["private", "govt", "disputed", "common"]),
                    verification_status=random.choice(["pending", "verified", "acquired"]),
                )
                db.add(parcel)
                parcels.append(parcel)
        db.flush()
        print(f"  Created {len(parcels)} land parcels")

        # === LAND OWNERS ===
        print("Seeding land owners...")
        for i, parcel in enumerate(parcels[:60]):
            owner_name = f"Land Owner Group {i//5 + 1}" if i < 20 else f"Family {i-19}" if i < 40 else f"Patel Family {i-39}"
            lo = LandOwner(
                parcel_id=parcel.id, full_name=owner_name,
                aadhaar_masked=f"{rand(1000, 9999):04d}****{rand(1000, 9999):04d}",
                phone=f"+91-98100-{rand(100, 999):03d}", email=f"owner{i}@email.com",
                bank_account_masked=f"*****{rand(10000, 99999):05d}",
                ifsc=f"SBIN{rand(0, 9)}{rand(100, 999)}{rand(100, 999)}",
                share_percentage=Decimal(str(round(random.uniform(5, 40), 2))),
                user_id=citizen_users[i % len(citizen_users)].id if i % 3 == 0 else None,
            )
            db.add(lo)
        db.flush()
        print("  Created land owners")

        # === SURVEY RECORDS ===
        print("Seeding survey records...")
        for i, parcel in enumerate(parcels[:40]):
            sr = SurveyRecord(
                parcel_id=parcel.id, surveyed_by=field_users[i % len(field_users)].id,
                survey_date=random_date(date(2023, 1, 1), date(2024, 12, 31)).strftime("%Y-%m-%d"),
                geo_lat=round(random.uniform(21.0, 21.5), 7),
                geo_lng=round(random.uniform(78.0, 79.5), 7),
                condition_notes=f"Survey notes for parcel {parcel.survey_number}",
                status=random.choice(["scheduled", "completed", "flagged"]),
            )
            db.add(sr)
        db.flush()
        print("  Created survey records")

        # === LEGAL NOTIFICATIONS ===
        print("Seeding legal notifications...")
        for i, proj in enumerate(projects[:10]):
            ln = LegalNotification(
                project_id=proj.id,
                section_type="Section 11" if i % 2 == 0 else "Section 19",
                notification_number=f"{'S11' if i % 2 == 0 else 'S19'}/NLAMS/{str(proj.id)[:8]}",
                issued_date=random_date(date(2023, 1, 1), date(2024, 12, 31)),
                status=random.choice(["draft", "issued", "challenged"]),
            )
            db.add(ln)
        db.flush()
        print("  Created legal notifications")

        # === OBJECTIONS ===
        print("Seeding objections...")
        for i, parcel in enumerate(parcels[:30]):
            obj_status = random.choice(["filed", "under_review", "resolved"])
            obj = Objection(
                parcel_id=parcel.id,
                filed_by=citizen_users[i % len(citizen_users)].id if i % 2 == 0 else None,
                filer_name=f"Land Owner Obj {i+1}",
                filer_contact=f"+91-98100-{rand(100, 999):03d}",
                objection_text=f"Objection regarding acquisition of parcel {parcel.survey_number} - insufficient compensation claimed",
                hearing_date=random_date(date(2024, 1, 1), date(2024, 12, 31)) if obj_status == "resolved" else None,
                status=obj_status,
                resolution_remarks=f"Objection resolved - compensation revised" if obj_status == "resolved" else None,
                resolved_by=district_users[i % len(district_users)].id if obj_status == "resolved" else None,
            )
            db.add(obj)
        db.flush()
        print("  Created objections")

        # === COMPENSATION ===
        print("Seeding compensation records...")
        comp_list = []
        for proj in [p1, p2, p5, p12]:
            project_parcels = [p for p in parcels if p.project_id == proj.id][:5]
            for parcel in project_parcels:
                area = parcel.area_hectares or Decimal("1.0")
                market_value = Decimal("500000") * area
                solatium = market_value
                additional = Decimal(str(round(random.uniform(0, float(market_value * 0.3)), 2)))
                total_award = market_value + solatium + additional
                comp = Compensation(
                    parcel_id=parcel.id, market_value=market_value, solatium=solatium,
                    additional_compensation=additional, total_award=total_award,
                    assessed_by=agency_users[0].id,
                    assessment_date=random_date(date(2023, 1, 1), date(2024, 6, 30)),
                    status=random.choice(["draft", "assessed", "approved"]),
                )
                db.add(comp)
                comp_list.append(comp)
        db.flush()
        print(f"  Created {len(comp_list)} compensation records")

        # === PAYMENTS ===
        print("Seeding payments...")
        for i, comp in enumerate(comp_list[:15]):
            lo = db.query(LandOwner).filter_by(parcel_id=comp.parcel_id).first()
            if lo:
                payment = Payment(
                    compensation_id=comp.id, land_owner_id=lo.id,
                    amount=comp.total_award or Decimal("15000000.00"),
                    pfms_reference=f"PFMS-{rand(100000, 999999):06d}",
                    bank_verification_status=random.choice(["pending", "verified", "failed"]),
                    payment_status=random.choice(["pending", "processing", "disbursed"]),
                )
                db.add(payment)
        db.flush()
        print("  Created payment records")

        # === R&R FAMILIES ===
        print("Seeding R&R records...")
        for proj in [p1, p2, p5, p12, p14]:
            parcel_count = len([p for p in parcels if p.project_id == proj.id])
            num_families = rand(max(5, parcel_count // 2), parcel_count + 10)
            for f in range(num_families):
                rr = RehabilitationFamily(
                    project_id=proj.id, family_head_name=f"Family Head {f+1}",
                    family_id_number=f"FF-{rand(1000, 9999):04d}",
                    member_count=rand(1, 8),
                    displaced_status=random.choice(["not_displaced", "partially", "fully"]),
                    housing_benefit_status=random.choice(["not_started", "in_progress", "provided"]),
                    employment_benefit_status=random.choice(["not_started", "in_progress", "provided"]),
                    monetary_benefit_amount=Decimal(str(round(random.uniform(50000, 500000), 2))),
                    current_stage=random.choice(["identification", "verification", "benefit_disbursement", "resettled"]),
                    progress_percentage=rand(0, 100),
                )
                db.add(rr)
        db.flush()
        print("  Created R&R records")

        # === DOCUMENTS ===
        print("Seeding documents...")
        doc_types = ["dpr", "survey_report", "notification", "award", "geojson", "photo", "other"]
        exts = ["pdf", "jpg", "geojson", "docx"]
        for i, proj in enumerate(projects[:10]):
            for d in range(rand(3, 7)):
                dt = random.choice(doc_types)
                ext = exts[d % 4]
                doc = Document(
                    project_id=proj.id, uploaded_by=agency_users[i % len(agency_users)].id,
                    doc_type=dt,
                    file_name=f"{proj.name.replace(' ', '_')}_{dt}_{d+1}.{ext}",
                    file_path=f"/uploads/documents/{proj.id}/{dt}/{proj.name.replace(' ', '_')}_{dt}_{d+1}.{ext}",
                    file_size=rand(100, 5000), mime_type=f"application/{ext}",
                    version=1,
                )
                db.add(doc)
        db.flush()
        print("  Created documents")

        # === AUDIT LOGS (flagship NH-44) ===
        print("Seeding audit trail for flagship project...")
        audit_entries = [
            ("created", None, {"name": p1.name, "stage": "project_proposal"}, "Project NH-44 Widening created"),
            ("updated", {"stage": "project_proposal"}, {"stage": "dpr_upload"}, "DPR uploaded and submitted"),
            ("updated", {"stage": "dpr_upload"}, {"stage": "land_requirement"}, "Land requirement assessment started"),
            ("updated", {"stage": "land_requirement"}, {"stage": "state_review"}, "State review initiated"),
            ("updated", {"stage": "state_review"}, {"stage": "district_verification"}, "District verification completed"),
            ("updated", {"stage": "district_verification"}, {"stage": "gis_mapping"}, "GIS mapping completed"),
            ("updated", {"stage": "gis_mapping"}, {"stage": "legal_notification"}, "Legal notification issued"),
            ("updated", {"stage": "legal_notification"}, {"stage": "objection_handling"}, "Objection handling phase started"),
            ("updated", {"stage": "objection_handling"}, {"stage": "compensation_assessment"}, "Compensation assessment completed"),
            ("updated", {"stage": "compensation_assessment"}, {"stage": "award_declaration"}, "Award declaration approved"),
            ("updated", {"stage": "award_declaration"}, {"stage": "payment_disbursement"}, "Payment disbursement initiated"),
            ("updated", {"stage": "payment_disbursement"}, {"stage": "physical_possession"}, "Physical possession taken"),
            ("updated", {"stage": "physical_possession"}, {"stage": "rehabilitation_resettlement"}, "R&R completed"),
            ("updated", {"stage": "rehabilitation_resettlement"}, {"stage": "project_completion"}, "Project officially completed"),
        ]
        for action, old_val, new_val, remarks in audit_entries:
            al = AuditLog(entity_type="project", entity_id=p1.id, action=action,
                         performed_by=sa.id, old_value=old_val, new_value=new_val,
                         remarks=remarks, ip_address=f"192.168.1.{rand(1, 254)}",
                         created_at=random_date(date(2022, 3, 15), date(2024, 12, 31)))
            db.add(al)
        db.flush()
        print(f"  Created {len(audit_entries)} audit log entries")

        # === NOTIFICATIONS ===
        print("Seeding in-app notifications...")
        for i, u in enumerate(all_users[:20]):
            n = NotificationApp(
                user_id=u.id,
                title=random.choice(["Project Updated", "New Assignment", "Compensation Approved", "Document Uploaded"]),
                body=f"You have a new notification regarding your project activities",
                type=random.choice(["info", "success", "warning"]),
                channel="in_app",
                is_read=random.choice([True, False]),
            )
            db.add(n)
        db.flush()
        print("  Created notifications")

        db.commit()
        print("\n" + "=" * 60)
        print("SEEDING COMPLETE!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  Roles: {len(roles)}")
        print(f"  Ministries: {len(ministries)}")
        print(f"  Categories: {len(categories)}")
        print(f"  States: {len(state_objects)}")
        print(f"  Users: {len(all_users)}")
        print(f"  Projects: {len(projects)}")
        print(f"  Parcels: {len(parcels)}")
        print(f"  Compensations: {len(comp_list)}")
        print(f"  Audit logs: {len(audit_entries)}")

    except Exception as e:
        db.rollback()
        print(f"\nERROR during seeding: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
