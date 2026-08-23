from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime, timezone
import uuid

from app.db.session import get_db
from app.models.project import Project, Milestone
from app.models.land import LandParcel
from app.models.compensation import Compensation
from app.models.legal import Objection
from app.models.document import Document
from app.models.circle_rate import CircleRate
from app.models.user import User
from app.core.deps import get_current_user

router = APIRouter(prefix="/ai", tags=["ai-insights"])


@router.get("/delay-prediction/{project_id}")
async def delay_prediction(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    ms_result = await db.execute(
        select(Milestone).where(Milestone.project_id == project_id).order_by(Milestone.planned_date)
    )
    milestones = ms_result.scalars().all()

    today = datetime.now(timezone.utc)
    delays = []
    at_risk = 0
    completed_count = 0

    for ms in milestones:
        if ms.status.value == "completed" if hasattr(ms.status, 'value') else ms.status == "completed":
            completed_count += 1
            if ms.planned_date and ms.actual_date:
                diff = (ms.actual_date - ms.planned_date).days
                if diff > 0:
                    delays.append(diff)
        elif ms.planned_date and ms.planned_date < today:
            at_risk += 1

    avg_delay = sum(delays) / len(delays) if delays else 0
    risk_factor = at_risk / max(len(milestones), 1)

    if risk_factor > 0.3 or avg_delay > 30:
        risk_label = "Delayed"
        color = "red"
        estimated_delay = int(avg_delay + 15)
    elif risk_factor > 0.1 or avg_delay > 10:
        risk_label = "At Risk"
        color = "orange"
        estimated_delay = int(avg_delay + 5)
    else:
        risk_label = "On Track"
        color = "green"
        estimated_delay = 0

    return {
        "project_id": str(project_id),
        "risk_label": risk_label,
        "color": color,
        "estimated_delay_days": estimated_delay,
        "total_milestones": len(milestones),
        "completed_milestones": completed_count,
        "at_risk_milestones": at_risk,
        "avg_historical_delay_days": round(avg_delay, 1),
        "reasoning": f"Based on {len(milestones)} milestones, {completed_count} completed, {at_risk} overdue. Average historical delay: {avg_delay:.0f} days.",
        "badge": "AI Insights • Beta",
    }


@router.get("/risk-score/{project_id}")
async def risk_score(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Open objections
    obj_result = await db.execute(
        select(func.count(Objection.id)).where(Objection.parcel_id.in_(
            select(LandParcel.id).where(LandParcel.project_id == project_id)
        ), Objection.status.in_(["filed", "under_review"]))
    )
    open_objections = obj_result.scalar() or 0

    # Disputed parcels
    disputed = (await db.execute(
        select(func.count(LandParcel.id)).where(
            LandParcel.project_id == project_id,
            LandParcel.verification_status == "disputed"
        )
    )).scalar() or 0

    total_parcels = (await db.execute(
        select(func.count(LandParcel.id)).where(LandParcel.project_id == project_id)
    )).scalar() or 1

    # Last milestone update
    last_ms = (await db.execute(
        select(Milestone).where(Milestone.project_id == project_id).order_by(Milestone.updated_at.desc())
    )).scalar_one_or_none()

    days_since_update = 0
    if last_ms and last_ms.updated_at:
        days_since_update = (datetime.now(timezone.utc) - last_ms.updated_at.replace(tzinfo=timezone.utc)).days

    # Score calculation
    score = 0
    score += min(open_objections * 10, 30)  # Max 30 for objections
    score += min((disputed / total_parcels) * 30, 30)  # Max 30 for disputes
    score += min(days_since_update * 2, 20)  # Max 20 for staleness
    score += (20 if project.status.value == "delayed" else 10 if project.status.value == "under_review" else 0)  # Status factor
    score = min(int(score), 100)

    if score >= 70:
        color = "red"
        label = "High Risk"
    elif score >= 40:
        color = "orange"
        label = "Medium Risk"
    else:
        color = "green"
        label = "Low Risk"

    return {
        "project_id": str(project_id),
        "score": score,
        "color": color,
        "label": label,
        "factors": {
            "open_objections": open_objections,
            "disputed_parcels": disputed,
            "total_parcels": total_parcels,
            "days_since_last_update": days_since_update,
            "current_status": project.status.value if hasattr(project.status, 'value') else str(project.status),
        },
        "badge": "AI Insights • Beta",
    }


@router.post("/compensation-estimate")
async def compensation_estimate(
    land_type: str,
    area_hectares: float,
    state_id: Optional[uuid.UUID] = None,
    district_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Look up circle rate
    query = select(CircleRate).where(CircleRate.land_type == land_type)
    if district_id:
        query = query.where(CircleRate.district_id == district_id)
    elif state_id:
        query = query.where(CircleRate.state_id == state_id)

    result = await db.execute(query.order_by(CircleRate.financial_year.desc()))
    rate = result.scalar_one_or_none()

    if rate:
        base_value = float(rate.rate_per_hectare) * area_hectares
    else:
        # Default rates per hectare (₹)
        defaults = {
            "agricultural": 500000, "residential": 2000000, "commercial": 5000000,
            "forest": 100000, "govt": 0, "other": 300000
        }
        base_value = defaults.get(land_type, 300000) * area_hectares

    solatium = base_value  # 100% per LARR Act 2013
    min_total = base_value + solatium
    max_total = base_value + solatium + (base_value * 0.3)  # Up to 30% additional

    return {
        "land_type": land_type,
        "area_hectares": area_hectares,
        "base_value": round(base_value, 2),
        "solatium": round(solatium, 2),
        "estimated_range_min": round(min_total, 2),
        "estimated_range_max": round(max_total, 2),
        "currency": "INR",
        "badge": "AI Insights • Beta",
        "note": "Estimate based on circle rates and LARR Act 2013 solatium provisions.",
    }


@router.get("/missing-documents/{project_id}")
async def missing_documents(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Required docs per stage
    stage_docs = {
        "dpr_upload": ["dpr"],
        "legal_notification": ["notification"],
        "compensation_assessment": ["award"],
        "award_declaration": ["award"],
        "project_completion": ["dpr", "award", "notification"],
    }

    # Get uploaded docs
    doc_result = await db.execute(
        select(Document.doc_type).where(Document.project_id == project_id).distinct()
    )
    uploaded = {row[0] for row in doc_result.all()}

    gaps = []
    required_for_stage = stage_docs.get(project.current_stage, [])
    for req in required_for_stage:
        if req not in uploaded:
            gaps.append(req)

    return {
        "project_id": str(project_id),
        "current_stage": project.current_stage,
        "uploaded_doc_types": list(uploaded),
        "missing_documents": gaps,
        "completeness_pct": round((len(required_for_stage) - len(gaps)) / max(len(required_for_stage), 1) * 100, 1),
        "badge": "AI Insights • Beta",
    }
