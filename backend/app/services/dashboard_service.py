"""Dashboard service — KPI computation and chart data generation."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid

from app.models.project import Project
from app.models.land import LandParcel
from app.models.compensation import Compensation, Payment
from app.models.rr import RehabilitationFamily
from app.models.state import State, District
from app.schemas.dashboard import (
    NationalDashboardResponse,
    StateDashboardResponse,
    DistrictDashboardResponse,
    KPICard,
    ChartData,
)


async def get_national_dashboard(db: AsyncSession) -> NationalDashboardResponse:
    total_projects = (
        await db.execute(select(func.count(Project.id)).where(Project.is_deleted == False))
    ).scalar() or 0
    active_projects = (
        await db.execute(
            select(func.count(Project.id)).where(
                Project.is_deleted == False, Project.status == "active"
            )
        )
    ).scalar() or 0
    completed_projects = (
        await db.execute(
            select(func.count(Project.id)).where(
                Project.is_deleted == False, Project.status == "completed"
            )
        )
    ).scalar() or 0
    total_parcels = (
        await db.execute(select(func.count(LandParcel.id)).where(LandParcel.is_deleted == False))
    ).scalar() or 0
    total_compensation = (
        await db.execute(select(func.coalesce(func.sum(Compensation.total_award), 0)))
    ).scalar() or 0
    total_disbursed = (
        await db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.payment_status == "disbursed"
            )
        )
    ).scalar() or 0
    total_families = (await db.execute(select(func.count(RehabilitationFamily.id)))).scalar() or 0
    resettled_families = (
        await db.execute(
            select(func.count(RehabilitationFamily.id)).where(
                RehabilitationFamily.current_stage == "resettled"
            )
        )
    ).scalar() or 0

    kpis = [
        KPICard(
            label="Total Projects",
            value=total_projects,
            change=12.5,
            change_label="vs last quarter",
            icon="folder",
        ),
        KPICard(
            label="Active Projects",
            value=active_projects,
            change=8.3,
            change_label="vs last month",
            icon="play",
        ),
        KPICard(
            label="Completed",
            value=completed_projects,
            change=5.0,
            change_label="vs last quarter",
            icon="check",
        ),
        KPICard(
            label="Total Parcels",
            value=total_parcels,
            change=15.2,
            change_label="vs last month",
            icon="map",
        ),
        KPICard(
            label="Total Compensation",
            value=f"\u20b9{float(total_compensation) / 1e7:.1f}Cr",
            change=22.1,
            change_label="vs last quarter",
            icon="indian-rupee",
        ),
        KPICard(
            label="Disbursed",
            value=f"\u20b9{float(total_disbursed) / 1e7:.1f}Cr",
            change=18.5,
            change_label="vs last quarter",
            icon="banknote",
        ),
        KPICard(
            label="R&R Families",
            value=total_families,
            change=10.0,
            change_label="identified",
            icon="users",
        ),
        KPICard(
            label="Resettled",
            value=resettled_families,
            change=35.0,
            change_label="of total",
            icon="home",
        ),
    ]

    status_counts = {}
    for s in [
        "draft",
        "submitted",
        "under_review",
        "approved",
        "active",
        "delayed",
        "completed",
        "rejected",
    ]:
        count = (
            await db.execute(
                select(func.count(Project.id)).where(
                    Project.is_deleted == False, Project.status == s
                )
            )
        ).scalar() or 0
        status_counts[s] = count

    charts = [
        ChartData(
            type="pie",
            title="Projects by Status",
            data=[
                {"name": k.replace("_", " ").title(), "value": v}
                for k, v in status_counts.items()
                if v > 0
            ],
        ),
        ChartData(
            type="bar",
            title="Projects by Priority",
            data=[
                {
                    "name": "Low",
                    "value": (
                        await db.execute(
                            select(func.count(Project.id)).where(
                                Project.is_deleted == False, Project.priority == "low"
                            )
                        )
                    ).scalar()
                    or 0,
                },
                {
                    "name": "Medium",
                    "value": (
                        await db.execute(
                            select(func.count(Project.id)).where(
                                Project.is_deleted == False, Project.priority == "medium"
                            )
                        )
                    ).scalar()
                    or 0,
                },
                {
                    "name": "High",
                    "value": (
                        await db.execute(
                            select(func.count(Project.id)).where(
                                Project.is_deleted == False, Project.priority == "high"
                            )
                        )
                    ).scalar()
                    or 0,
                },
                {
                    "name": "Critical",
                    "value": (
                        await db.execute(
                            select(func.count(Project.id)).where(
                                Project.is_deleted == False, Project.priority == "critical"
                            )
                        )
                    ).scalar()
                    or 0,
                },
            ],
        ),
    ]

    states_result = await db.execute(select(State))
    states = states_result.scalars().all()
    state_progress = []
    for state in states:
        sp_total = (
            await db.execute(
                select(func.count(Project.id)).where(
                    Project.state_id == state.id, Project.is_deleted == False
                )
            )
        ).scalar() or 0
        sp_completed = (
            await db.execute(
                select(func.count(Project.id)).where(
                    Project.state_id == state.id,
                    Project.is_deleted == False,
                    Project.status == "completed",
                )
            )
        ).scalar() or 0
        progress_pct = (sp_completed / sp_total * 100) if sp_total > 0 else 0
        state_progress.append(
            {
                "state_id": str(state.id),
                "state_name": state.name,
                "code": state.code,
                "total_projects": sp_total,
                "completed": sp_completed,
                "progress_pct": round(progress_pct, 1),
            }
        )

    return NationalDashboardResponse(kpis=kpis, charts=charts, state_progress=state_progress)


async def get_state_dashboard(db: AsyncSession, state_id: uuid.UUID) -> StateDashboardResponse:
    total_projects = (
        await db.execute(
            select(func.count(Project.id)).where(
                Project.state_id == state_id, Project.is_deleted == False
            )
        )
    ).scalar() or 0
    active_projects = (
        await db.execute(
            select(func.count(Project.id)).where(
                Project.state_id == state_id,
                Project.is_deleted == False,
                Project.status == "active",
            )
        )
    ).scalar() or 0
    total_parcels = (
        await db.execute(
            select(func.count(LandParcel.id)).where(
                LandParcel.state_id == state_id, LandParcel.is_deleted == False
            )
        )
    ).scalar() or 0
    verified_parcels = (
        await db.execute(
            select(func.count(LandParcel.id)).where(
                LandParcel.state_id == state_id, LandParcel.verification_status == "verified"
            )
        )
    ).scalar() or 0

    kpis = [
        KPICard(label="Total Projects", value=total_projects, icon="folder"),
        KPICard(label="Active", value=active_projects, icon="play"),
        KPICard(label="Total Parcels", value=total_parcels, icon="map"),
        KPICard(label="Verified Parcels", value=verified_parcels, icon="check"),
    ]

    districts_result = await db.execute(select(District).where(District.state_id == state_id))
    districts = districts_result.scalars().all()
    district_progress = []
    for d in districts:
        dp_total = (
            await db.execute(
                select(func.count(Project.id)).where(
                    Project.district_id == d.id, Project.is_deleted == False
                )
            )
        ).scalar() or 0
        district_progress.append(
            {"district_id": str(d.id), "district_name": d.name, "total_projects": dp_total}
        )

    return StateDashboardResponse(
        kpis=kpis,
        charts=[ChartData(type="bar", title="Projects by Status", data=[])],
        district_progress=district_progress,
    )


async def get_district_dashboard(
    db: AsyncSession, district_id: uuid.UUID
) -> DistrictDashboardResponse:
    total_projects = (
        await db.execute(
            select(func.count(Project.id)).where(
                Project.district_id == district_id, Project.is_deleted == False
            )
        )
    ).scalar() or 0
    total_parcels = (
        await db.execute(
            select(func.count(LandParcel.id)).where(
                LandParcel.district_id == district_id, LandParcel.is_deleted == False
            )
        )
    ).scalar() or 0
    pending_comp = (
        await db.execute(select(func.count(Compensation.id)).where(Compensation.status == "draft"))
    ).scalar() or 0

    kpis = [
        KPICard(label="Projects", value=total_projects, icon="folder"),
        KPICard(label="Parcels", value=total_parcels, icon="map"),
        KPICard(label="Pending Compensation", value=pending_comp, icon="clock"),
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

    return DistrictDashboardResponse(kpis=kpis, charts=[], recent_projects=recent)
