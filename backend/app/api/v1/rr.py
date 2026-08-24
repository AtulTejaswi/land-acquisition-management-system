from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import uuid

from app.db.session import get_db
from app.models.rr import RehabilitationFamily
from app.models.project import Project
from app.models.user import User
from app.models.audit import AuditLog
from app.core.deps import require_role, get_current_user
from app.schemas.rr import (
    RRFamilyCreate,
    RRFamilyUpdate,
    RRFamilyResponse,
    PaginatedRRFamilies,
    RRProjectSummary,
)

router = APIRouter(prefix="/rr", tags=["rehabilitation-resettlement"])


@router.get("/families", response_model=PaginatedRRFamilies)
async def list_rr_families(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    project_id: Optional[uuid.UUID] = None,
    displaced_status: Optional[str] = None,
    current_stage: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(RehabilitationFamily)
    count_query = select(func.count(RehabilitationFamily.id))

    if project_id:
        query = query.where(RehabilitationFamily.project_id == project_id)
        count_query = count_query.where(RehabilitationFamily.project_id == project_id)
    if displaced_status:
        query = query.where(RehabilitationFamily.displaced_status == displaced_status)
        count_query = count_query.where(RehabilitationFamily.displaced_status == displaced_status)
    if current_stage:
        query = query.where(RehabilitationFamily.current_stage == current_stage)
        count_query = count_query.where(RehabilitationFamily.current_stage == current_stage)

    total = (await db.execute(count_query)).scalar()
    query = (
        query.order_by(RehabilitationFamily.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    items = result.scalars().all()
    return PaginatedRRFamilies(
        items=[RRFamilyResponse.model_validate(f) for f in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/families/{family_id}", response_model=RRFamilyResponse)
async def get_rr_family(
    family_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RehabilitationFamily).where(RehabilitationFamily.id == family_id)
    )
    family = result.scalar_one_or_none()
    if not family:
        raise HTTPException(status_code=404, detail="RR Family not found")
    return RRFamilyResponse.model_validate(family)


@router.post("/families", response_model=RRFamilyResponse, status_code=status.HTTP_201_CREATED)
async def create_rr_family(
    data: RRFamilyCreate,
    current_user: User = Depends(
        require_role(["super_admin", "state_authority", "district_officer"])
    ),
    db: AsyncSession = Depends(get_db),
):
    family = RehabilitationFamily(**data.model_dump())
    db.add(family)
    await db.flush()

    # Audit log
    audit = AuditLog(
        entity_type="rr_family",
        entity_id=family.id,
        action="create",
        performed_by=current_user.id,
        new_value=data.model_dump(),
        remarks="R&R family record created",
    )
    db.add(audit)
    await db.commit()
    await db.refresh(family)
    return RRFamilyResponse.model_validate(family)


@router.patch("/families/{family_id}", response_model=RRFamilyResponse)
async def update_rr_family(
    family_id: uuid.UUID,
    data: RRFamilyUpdate,
    current_user: User = Depends(
        require_role(["super_admin", "state_authority", "district_officer"])
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RehabilitationFamily).where(RehabilitationFamily.id == family_id)
    )
    family = result.scalar_one_or_none()
    if not family:
        raise HTTPException(status_code=404, detail="RR Family not found")

    old_value = {
        "displaced_status": family.displaced_status,
        "housing_benefit_status": family.housing_benefit_status,
        "employment_benefit_status": family.employment_benefit_status,
        "current_stage": family.current_stage,
        "progress_percentage": family.progress_percentage,
    }

    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(family, key, value)

    # Audit log
    audit = AuditLog(
        entity_type="rr_family",
        entity_id=family.id,
        action="update",
        performed_by=current_user.id,
        old_value=old_value,
        new_value=update_dict,
        remarks=f"R&R family record updated: {', '.join(update_dict.keys())}",
    )
    db.add(audit)
    await db.commit()
    await db.refresh(family)
    return RRFamilyResponse.model_validate(family)


@router.get("/summary", response_model=list[RRProjectSummary])
async def get_rr_summary(
    project_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get R&R status summary per project."""
    query = select(RehabilitationFamily)
    if project_id:
        query = query.where(RehabilitationFamily.project_id == project_id)
    result = await db.execute(query)
    families = result.scalars().all()

    # Group by project
    by_project: dict = {}
    for f in families:
        pid = f.project_id
        if pid not in by_project:
            by_project[pid] = {
                "project_id": pid,
                "project_name": "",
                "total_families": 0,
                "fully_displaced": 0,
                "partially_displaced": 0,
                "housing_provided": 0,
                "employment_provided": 0,
                "resettled": 0,
                "progress_values": [],
            }
        bp = by_project[pid]
        bp["total_families"] += 1
        if f.displaced_status == "fully":
            bp["fully_displaced"] += 1
        elif f.displaced_status == "partially":
            bp["partially_displaced"] += 1
        if f.housing_benefit_status == "provided":
            bp["housing_provided"] += 1
        if f.employment_benefit_status == "provided":
            bp["employment_provided"] += 1
        if f.current_stage == "resettled":
            bp["resettled"] += 1
        if f.progress_percentage is not None:
            bp["progress_values"].append(f.progress_percentage)

    # Resolve project names
    summaries = []
    for pid, bp in by_project.items():
        proj_result = await db.execute(select(Project).where(Project.id == pid))
        proj = proj_result.scalar_one_or_none()
        progress_vals = bp.pop("progress_values")
        summaries.append(
            RRProjectSummary(
                project_id=pid,
                project_name=proj.name if proj else "Unknown",
                total_families=bp["total_families"],
                fully_displaced=bp["fully_displaced"],
                partially_displaced=bp["partially_displaced"],
                housing_provided=bp["housing_provided"],
                employment_provided=bp["employment_provided"],
                resettled=bp["resettled"],
                avg_progress=(
                    round(sum(progress_vals) / len(progress_vals), 1) if progress_vals else 0
                ),
            )
        )
    return summaries
