"""AI Insights Service — rule-based algorithms for demo purposes.

All logic here is deterministic formulas, not real ML. Clearly labeled as
'AI Insights • Beta' in the UI. Per spec D4, these use milestone data,
objection counts, and circle rates.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone
import uuid

from app.models.project import Project, Milestone
from app.models.land import LandParcel
from app.models.legal import Objection
from app.models.document import Document
from app.models.circle_rate import CircleRate


async def compute_delay_prediction(db: AsyncSession, project_id: uuid.UUID) -> dict:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        return None

    ms_result = await db.execute(
        select(Milestone).where(Milestone.project_id == project_id).order_by(Milestone.planned_date)
    )
    milestones = ms_result.scalars().all()

    today = datetime.now(timezone.utc)
    delays = []
    at_risk = 0
    completed_count = 0

    for ms in milestones:
        ms_status = ms.status.value if hasattr(ms.status, "value") else ms.status
        if ms_status == "completed":
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
        "reasoning": (
            f"Based on {len(milestones)} milestones, {completed_count} completed, "
            f"{at_risk} overdue. Average historical delay: {avg_delay:.0f} days."
        ),
        "badge": "AI Insights • Beta",
    }


async def compute_risk_score(db: AsyncSession, project_id: uuid.UUID) -> dict:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        return None

    obj_result = await db.execute(
        select(func.count(Objection.id)).where(
            Objection.parcel_id.in_(
                select(LandParcel.id).where(LandParcel.project_id == project_id)
            ),
            Objection.status.in_(["filed", "under_review"]),
        )
    )
    open_objections = obj_result.scalar() or 0

    disputed = (
        await db.execute(
            select(func.count(LandParcel.id)).where(
                LandParcel.project_id == project_id,
                LandParcel.verification_status == "disputed",
            )
        )
    ).scalar() or 0

    total_parcels = (
        await db.execute(
            select(func.count(LandParcel.id)).where(LandParcel.project_id == project_id)
        )
    ).scalar() or 1

    last_ms = (
        await db.execute(
            select(Milestone)
            .where(Milestone.project_id == project_id)
            .order_by(Milestone.updated_at.desc())
        )
    ).scalar_one_or_none()

    days_since_update = 0
    if last_ms and last_ms.updated_at:
        days_since_update = (
            datetime.now(timezone.utc) - last_ms.updated_at.replace(tzinfo=timezone.utc)
        ).days

    score = 0
    score += min(open_objections * 10, 30)
    score += min((disputed / total_parcels) * 30, 30)
    score += min(days_since_update * 2, 20)
    proj_status = project.status.value if hasattr(project.status, "value") else str(project.status)
    score += 20 if proj_status == "delayed" else (10 if proj_status == "under_review" else 0)
    score = min(int(score), 100)

    if score >= 70:
        color, label = "red", "High Risk"
    elif score >= 40:
        color, label = "orange", "Medium Risk"
    else:
        color, label = "green", "Low Risk"

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
            "current_status": proj_status,
        },
        "badge": "AI Insights • Beta",
    }


async def estimate_compensation(
    db: AsyncSession,
    land_type: str,
    area_hectares: float,
    state_id: uuid.UUID | None = None,
    district_id: uuid.UUID | None = None,
) -> dict:
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
        defaults = {
            "agricultural": 500000,
            "residential": 2000000,
            "commercial": 5000000,
            "forest": 100000,
            "govt": 0,
            "other": 300000,
        }
        base_value = defaults.get(land_type, 300000) * area_hectares

    solatium = base_value
    min_total = base_value + solatium
    max_total = base_value + solatium + (base_value * 0.3)

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


async def detect_missing_documents(db: AsyncSession, project_id: uuid.UUID) -> dict:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        return None

    stage_docs = {
        "dpr_upload": ["dpr"],
        "legal_notification": ["notification"],
        "compensation_assessment": ["award"],
        "award_declaration": ["award"],
        "project_completion": ["dpr", "award", "notification"],
    }

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
        "completeness_pct": round(
            (len(required_for_stage) - len(gaps)) / max(len(required_for_stage), 1) * 100, 1
        ),
        "badge": "AI Insights • Beta",
    }
