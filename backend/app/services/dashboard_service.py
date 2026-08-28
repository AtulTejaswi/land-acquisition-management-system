"""Dashboard service — KPI computation and chart data generation.

Updated to compute from real Odisha (Khordha) data instead of multi-state demo data.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid

from app.models.project import Project
from app.models.land import LandParcel, LandOwner
from app.models.compensation import Compensation, Payment
from app.models.rr import RehabilitationFamily
from app.models.state import State, District, Village
from app.schemas.dashboard import (
    NationalDashboardResponse,
    StateDashboardResponse,
    DistrictDashboardResponse,
    KPICard,
    ChartData,
)


async def get_national_dashboard(db: AsyncSession) -> NationalDashboardResponse:
    """National dashboard — now shows single-state (Odisha) overview with real data."""

    # KPIs from real data
    total_parcels = (
        await db.execute(select(func.count(LandParcel.id)).where(LandParcel.is_deleted == False))
    ).scalar() or 0

    total_owners = (await db.execute(select(func.count(LandOwner.id)))).scalar() or 0

    total_area = (
        await db.execute(
            select(func.coalesce(func.sum(LandParcel.area_hectares), 0)).where(
                LandParcel.is_deleted == False
            )
        )
    ).scalar() or 0

    # Count co-owned parcels (>1 owner)
    co_owned_subq = (
        select(LandOwner.parcel_id, func.count(LandOwner.id).label("owner_count"))
        .group_by(LandOwner.parcel_id)
        .having(func.count(LandOwner.id) > 1)
        .subquery()
    )
    co_owned_count = (
        await db.execute(select(func.count()).select_from(co_owned_subq))
    ).scalar() or 0

    govt_area = (
        await db.execute(
            select(func.coalesce(func.sum(LandParcel.area_hectares), 0)).where(
                LandParcel.is_deleted == False, LandParcel.ownership_status == "govt"
            )
        )
    ).scalar() or 0

    private_area = (
        await db.execute(
            select(func.coalesce(func.sum(LandParcel.area_hectares), 0)).where(
                LandParcel.is_deleted == False, LandParcel.ownership_status == "private"
            )
        )
    ).scalar() or 0

    total_compensation = (
        await db.execute(select(func.coalesce(func.sum(Compensation.total_award), 0)))
    ).scalar() or 0

    total_families = (await db.execute(select(func.count(RehabilitationFamily.id)))).scalar() or 0

    kpis = [
        KPICard(
            label="Total Parcels",
            value=total_parcels,
            change=None,
            change_label="Khordha district",
            icon="map",
        ),
        KPICard(
            label="Total Area",
            value=f"{float(total_area):.2f} ha",
            change=None,
            change_label="surveyed area",
            icon="ruler",
        ),
        KPICard(
            label="Total Owners",
            value=total_owners,
            change=None,
            change_label="registered parties",
            icon="users",
        ),
        KPICard(
            label="Co-owned Parcels",
            value=co_owned_count,
            change=round(co_owned_count / total_parcels * 100, 1) if total_parcels else 0,
            change_label="% of total parcels",
            icon="users",
        ),
        KPICard(
            label="Government Land",
            value=f"{float(govt_area):.2f} ha",
            change=None,
            change_label="area",
            icon="building",
        ),
        KPICard(
            label="Private Land",
            value=f"{float(private_area):.2f} ha",
            change=None,
            change_label="area",
            icon="home",
        ),
        KPICard(
            label="Total Compensation",
            value=f"\u20b9{float(total_compensation) / 1e7:.1f}Cr" if total_compensation else "\u20b90",
            change=None,
            change_label="assessed",
            icon="indian-rupee",
        ),
        KPICard(
            label="R&R Families",
            value=total_families,
            change=None,
            change_label="identified",
            icon="users",
        ),
    ]

    # Charts: Parcel count by village (real data)
    village_parcels = []
    villages_result = await db.execute(
        select(Village.name, func.count(LandParcel.id).label("count"))
        .join(LandParcel, LandParcel.village_id == Village.id)
        .where(LandParcel.is_deleted == False)
        .group_by(Village.name)
        .order_by(func.count(LandParcel.id).desc())
    )
    for name, count in villages_result.all():
        village_parcels.append({"name": name, "value": count})

    # Charts: Ownership split (government vs private by area)
    ownership_data = []
    for status_label, status_val in [("Government", "govt"), ("Private", "private")]:
        area = (
            await db.execute(
                select(func.coalesce(func.sum(LandParcel.area_hectares), 0)).where(
                    LandParcel.is_deleted == False, LandParcel.ownership_status == status_val
                )
            )
        ).scalar() or 0
        ownership_data.append({"name": status_label, "value": round(float(area), 4)})

    # Charts: Land type distribution
    land_type_data = []
    lt_result = await db.execute(
        select(LandParcel.land_type, func.count(LandParcel.id).label("count"))
        .where(LandParcel.is_deleted == False)
        .group_by(LandParcel.land_type)
    )
    for lt, count in lt_result.all():
        land_type_data.append({
            "name": lt.value if hasattr(lt, "value") else str(lt),
            "value": count,
        })

    # Charts: Owner count distribution
    owner_dist = []
    for n_owners in [1, 2, 3, 4, 5]:
        count = (
            await db.execute(
                select(func.count()).select_from(
                    select(LandOwner.parcel_id, func.count(LandOwner.id).label("cnt"))
                    .group_by(LandOwner.parcel_id)
                    .having(func.count(LandOwner.id) == n_owners)
                    .subquery()
                )
            )
        ).scalar() or 0
        if count > 0:
            owner_dist.append({"name": f"{n_owners} owner{'s' if n_owners > 1 else ''}", "value": count})

    charts = [
        ChartData(type="bar", title="Parcels by Village", data=village_parcels),
        ChartData(type="pie", title="Area by Ownership (ha)", data=ownership_data),
        ChartData(type="pie", title="Land Type Distribution", data=land_type_data),
        ChartData(type="bar", title="Co-ownership Distribution", data=owner_dist),
    ]

    # State progress — show Odisha as the only state
    states_result = await db.execute(select(State))
    states = states_result.scalars().all()
    state_progress = []
    for state in states:
        sp_total = (
            await db.execute(
                select(func.count(LandParcel.id)).where(
                    LandParcel.state_id == state.id, LandParcel.is_deleted == False
                )
            )
        ).scalar() or 0
        state_progress.append(
            {
                "state_id": str(state.id),
                "state_name": state.name,
                "code": state.code,
                "total_projects": sp_total,
                "completed": sp_total,  # All imported parcels count as "onboarded"
                "progress_pct": 100.0,
            }
        )

    return NationalDashboardResponse(kpis=kpis, charts=charts, state_progress=state_progress)


async def get_state_dashboard(db: AsyncSession, state_id: uuid.UUID) -> StateDashboardResponse:
    """State dashboard for Odisha — real parcel/owner data from bhoomirashi import."""

    total_parcels = (
        await db.execute(
            select(func.count(LandParcel.id)).where(
                LandParcel.state_id == state_id, LandParcel.is_deleted == False
            )
        )
    ).scalar() or 0

    total_area = (
        await db.execute(
            select(func.coalesce(func.sum(LandParcel.area_hectares), 0)).where(
                LandParcel.state_id == state_id, LandParcel.is_deleted == False
            )
        )
    ).scalar() or 0

    total_owners = (
        await db.execute(
            select(func.count(LandOwner.id))
            .join(LandParcel, LandOwner.parcel_id == LandParcel.id)
            .where(LandParcel.state_id == state_id)
        )
    ).scalar() or 0

    verified_parcels = (
        await db.execute(
            select(func.count(LandParcel.id)).where(
                LandParcel.state_id == state_id,
                LandParcel.is_deleted == False,
                LandParcel.verification_status == "verified",
            )
        )
    ).scalar() or 0

    kpis = [
        KPICard(label="Total Parcels", value=total_parcels, icon="map"),
        KPICard(label="Total Area", value=f"{float(total_area):.2f} ha", icon="ruler"),
        KPICard(label="Total Owners", value=total_owners, icon="users"),
        KPICard(label="Verified", value=verified_parcels, icon="check"),
    ]

    # Village-level charts
    village_parcels = []
    village_result = await db.execute(
        select(Village.name, func.count(LandParcel.id).label("count"))
        .join(LandParcel, LandParcel.village_id == Village.id)
        .where(LandParcel.state_id == state_id, LandParcel.is_deleted == False)
        .group_by(Village.name)
        .order_by(func.count(LandParcel.id).desc())
    )
    for name, count in village_result.all():
        village_parcels.append({"name": name, "value": count})

    village_area = []
    village_area_result = await db.execute(
        select(Village.name, func.coalesce(func.sum(LandParcel.area_hectares), 0).label("area"))
        .join(LandParcel, LandParcel.village_id == Village.id)
        .where(LandParcel.state_id == state_id, LandParcel.is_deleted == False)
        .group_by(Village.name)
        .order_by(func.sum(LandParcel.area_hectares).desc())
    )
    for name, area in village_area_result.all():
        village_area.append({"name": name, "value": round(float(area), 4)})

    # Ownership split
    ownership_data = []
    for status_label, status_val in [("Government", "govt"), ("Private", "private")]:
        area = (
            await db.execute(
                select(func.coalesce(func.sum(LandParcel.area_hectares), 0)).where(
                    LandParcel.state_id == state_id,
                    LandParcel.is_deleted == False,
                    LandParcel.ownership_status == status_val,
                )
            )
        ).scalar() or 0
        ownership_data.append({"name": status_label, "value": round(float(area), 4)})

    charts = [
        ChartData(type="bar", title="Parcels by Village", data=village_parcels),
        ChartData(type="bar", title="Area (ha) by Village", data=village_area),
        ChartData(type="pie", title="Area by Ownership", data=ownership_data),
    ]

    # District progress
    districts_result = await db.execute(
        select(District).where(District.state_id == state_id)
    )
    districts = districts_result.scalars().all()
    district_progress = []
    for d in districts:
        dp_total = (
            await db.execute(
                select(func.count(LandParcel.id)).where(
                    LandParcel.district_id == d.id, LandParcel.is_deleted == False
                )
            )
        ).scalar() or 0
        dp_area = (
            await db.execute(
                select(func.coalesce(func.sum(LandParcel.area_hectares), 0)).where(
                    LandParcel.district_id == d.id, LandParcel.is_deleted == False
                )
            )
        ).scalar() or 0
        district_progress.append({
            "district_id": str(d.id),
            "district_name": d.name,
            "total_parcels": dp_total,
            "total_area_ha": round(float(dp_area), 4),
        })

    return StateDashboardResponse(
        kpis=kpis,
        charts=charts,
        district_progress=district_progress,
    )


async def get_district_dashboard(
    db: AsyncSession, district_id: uuid.UUID
) -> DistrictDashboardResponse:
    """District dashboard for Khordha — real parcel/owner data."""

    total_parcels = (
        await db.execute(
            select(func.count(LandParcel.id)).where(
                LandParcel.district_id == district_id, LandParcel.is_deleted == False
            )
        )
    ).scalar() or 0

    total_area = (
        await db.execute(
            select(func.coalesce(func.sum(LandParcel.area_hectares), 0)).where(
                LandParcel.district_id == district_id, LandParcel.is_deleted == False
            )
        )
    ).scalar() or 0

    total_owners = (
        await db.execute(
            select(func.count(LandOwner.id))
            .join(LandParcel, LandOwner.parcel_id == LandParcel.id)
            .where(LandParcel.district_id == district_id)
        )
    ).scalar() or 0

    pending_comp = (
        await db.execute(
            select(func.count(Compensation.id)).where(Compensation.status == "draft")
        )
    ).scalar() or 0

    kpis = [
        KPICard(label="Parcels", value=total_parcels, icon="map"),
        KPICard(label="Total Area", value=f"{float(total_area):.2f} ha", icon="ruler"),
        KPICard(label="Owners", value=total_owners, icon="users"),
        KPICard(label="Pending Compensation", value=pending_comp, icon="clock"),
    ]

    # Village breakdown
    village_data = []
    village_result = await db.execute(
        select(Village.name, func.count(LandParcel.id).label("count"))
        .join(LandParcel, LandParcel.village_id == Village.id)
        .where(LandParcel.district_id == district_id, LandParcel.is_deleted == False)
        .group_by(Village.name)
        .order_by(func.count(LandParcel.id).desc())
    )
    for name, count in village_result.all():
        village_data.append({"name": name, "value": count})

    charts = [
        ChartData(type="bar", title="Parcels by Village", data=village_data),
    ]

    result = await db.execute(
        select(Project)
        .where(Project.district_id == district_id, Project.is_deleted == False)
        .order_by(Project.updated_at.desc())
        .limit(10)
    )
    recent = [
        {
            "id": str(p.id),
            "name": p.name,
            "status": p.status.value if hasattr(p.status, "value") else str(p.status),
        }
        for p in result.scalars().all()
    ]

    return DistrictDashboardResponse(kpis=kpis, charts=charts, recent_projects=recent)
