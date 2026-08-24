from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional
import uuid
import csv
import io
from datetime import datetime

from app.db.session import get_db
from app.models.project import Project
from app.models.compensation import Compensation, Payment
from app.models.land import LandParcel
from app.models.user import User
from app.core.deps import require_role

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/mis")
async def generate_mis_report(
    state_id: Optional[uuid.UUID] = None,
    district_id: Optional[uuid.UUID] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    format: str = "csv",
    current_user: User = Depends(require_role(["super_admin", "state_authority"])),
    db: AsyncSession = Depends(get_db),
):
    query = select(Project).where(Project.is_deleted == False)
    if state_id:
        query = query.where(Project.state_id == state_id)
    if district_id:
        query = query.where(Project.district_id == district_id)
    if status_filter:
        query = query.where(Project.status == status_filter)

    query = query.options(
        selectinload(Project.state),
        selectinload(Project.district),
    )
    result = await db.execute(query.order_by(Project.created_at.desc()))
    projects = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Project Name",
            "Status",
            "Priority",
            "Current Stage",
            "Estimated Budget (₹)",
            "State",
            "District",
            "Created At",
            "Target Completion",
        ]
    )

    for p in projects:
        writer.writerow(
            [
                p.name,
                p.status.value if hasattr(p.status, "value") else str(p.status),
                p.priority.value if hasattr(p.priority, "value") else str(p.priority),
                p.current_stage,
                float(p.estimated_budget) if p.estimated_budget else "",
                p.state.name if p.state else "",
                p.district.name if p.district else "",
                p.created_at.strftime("%Y-%m-%d") if p.created_at else "",
                p.target_completion_date.strftime("%Y-%m-%d") if p.target_completion_date else "",
            ]
        )

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=MIS_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        },
    )


@router.get("/compensation")
async def generate_compensation_report(
    state_id: Optional[uuid.UUID] = None,
    district_id: Optional[uuid.UUID] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    format: str = "csv",
    current_user: User = Depends(require_role(["super_admin", "state_authority"])),
    db: AsyncSession = Depends(get_db),
):
    """CSV export of all compensation assessments, awards, and payment disbursements."""
    query = select(Compensation).options(
        selectinload(Compensation.parcel), selectinload(Compensation.payments)
    )
    count_query = select(func.count(Compensation.id))

    # Filter by state/district through the parcel relationship
    if state_id:
        query = query.join(LandParcel, Compensation.parcel_id == LandParcel.id).where(
            LandParcel.state_id == state_id
        )
        count_query = count_query.join(LandParcel, Compensation.parcel_id == LandParcel.id).where(
            LandParcel.state_id == state_id
        )
    if district_id:
        query = query.join(LandParcel, Compensation.parcel_id == LandParcel.id).where(
            LandParcel.district_id == district_id
        )
        count_query = count_query.join(LandParcel, Compensation.parcel_id == LandParcel.id).where(
            LandParcel.district_id == district_id
        )
    if status_filter:
        query = query.where(Compensation.status == status_filter)
        count_query = count_query.where(Compensation.status == status_filter)

    result = await db.execute(query.order_by(Compensation.created_at.desc()))
    compensations = result.scalars().unique().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Parcel ID",
            "Market Value (₹)",
            "Solatium (₹)",
            "Additional Compensation (₹)",
            "Total Award (₹)",
            "Status",
            "Assessment Date",
            "Payments Count",
            "Total Disbursed (₹)",
            "Created At",
        ]
    )

    for c in compensations:
        total_disbursed = sum(
            float(p.amount) for p in (c.payments or []) if p.payment_status == "disbursed"
        )
        writer.writerow(
            [
                str(c.parcel_id),
                float(c.market_value) if c.market_value else "",
                float(c.solatium) if c.solatium else "",
                float(c.additional_compensation) if c.additional_compensation else "",
                float(c.total_award) if c.total_award else "",
                c.status.value if hasattr(c.status, "value") else str(c.status),
                c.assessment_date.strftime("%Y-%m-%d") if c.assessment_date else "",
                len(c.payments or []),
                round(total_disbursed, 2),
                c.created_at.strftime("%Y-%m-%d") if c.created_at else "",
            ]
        )

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=Compensation_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        },
    )


@router.get("/gis-parcels")
async def generate_gis_parcels_report(
    state_id: Optional[uuid.UUID] = None,
    district_id: Optional[uuid.UUID] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    format: str = "csv",
    current_user: User = Depends(require_role(["super_admin", "state_authority"])),
    db: AsyncSession = Depends(get_db),
):
    """CSV export of land parcel inventory with verification status and area details."""
    query = (
        select(LandParcel)
        .where(LandParcel.is_deleted == False)
        .options(
            selectinload(LandParcel.village),
            selectinload(LandParcel.district),
            selectinload(LandParcel.state),
            selectinload(LandParcel.project),
        )
    )

    if state_id:
        query = query.where(LandParcel.state_id == state_id)
    if district_id:
        query = query.where(LandParcel.district_id == district_id)
    if status_filter:
        query = query.where(LandParcel.verification_status == status_filter)

    result = await db.execute(query.order_by(LandParcel.created_at.desc()))
    parcels = result.scalars().unique().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Survey Number",
            "Village",
            "District",
            "State",
            "Area (Hectares)",
            "Land Type",
            "Ownership Status",
            "Verification Status",
            "Linked Project",
            "Created At",
        ]
    )

    for p in parcels:
        writer.writerow(
            [
                p.survey_number,
                p.village.name if p.village else "",
                p.district.name if p.district else "",
                p.state.name if p.state else "",
                float(p.area_hectares) if p.area_hectares else "",
                p.land_type.value if hasattr(p.land_type, "value") else str(p.land_type),
                p.ownership_status.value
                if hasattr(p.ownership_status, "value")
                else str(p.ownership_status),
                p.verification_status.value
                if hasattr(p.verification_status, "value")
                else str(p.verification_status),
                p.project.name if p.project else "",
                p.created_at.strftime("%Y-%m-%d") if p.created_at else "",
            ]
        )

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=GIS_Parcels_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        },
    )
