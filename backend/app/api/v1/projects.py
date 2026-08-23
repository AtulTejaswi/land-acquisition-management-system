from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import datetime, timezone
import uuid

from app.db.session import get_db
from app.models.project import Project, Milestone, Ministry, ProjectCategory, ProjectStatus, MilestoneStatus, STAGES
from app.models.user import User
from app.models.audit import AuditLog
from app.core.deps import require_role, get_current_user
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse, PaginatedProjects,
    MilestoneCreate, MilestoneUpdate, MilestoneResponse,
    MinistryResponse, CategoryResponse
)

router = APIRouter(prefix="/projects", tags=["projects"])


def project_to_response(p: Project) -> ProjectResponse:
    return ProjectResponse(
        id=p.id, name=p.name,
        ministry_id=p.ministry_id, category_id=p.category_id,
        implementing_agency_id=p.implementing_agency_id,
        state_id=p.state_id, district_id=p.district_id,
        description=p.description,
        estimated_budget=float(p.estimated_budget) if p.estimated_budget else None,
        estimated_land_required_hectares=float(p.estimated_land_required_hectares) if p.estimated_land_required_hectares else None,
        priority=p.priority.value if hasattr(p.priority, 'value') else str(p.priority),
        current_stage=p.current_stage,
        status=p.status.value if hasattr(p.status, 'value') else str(p.status),
        start_date=p.start_date, target_completion_date=p.target_completion_date,
        created_by=p.created_by, created_at=p.created_at, updated_at=p.updated_at,
        ministry_name=p.ministry.name if p.ministry else None,
        category_name=p.category.name if p.category else None,
        state_name=p.state.name if p.state else None,
        district_name=p.district.name if p.district else None,
        created_by_name=p.creator.full_name if hasattr(p, 'creator') and p.creator else None,
    )


@router.get("", response_model=PaginatedProjects)
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    state_id: Optional[uuid.UUID] = None,
    district_id: Optional[uuid.UUID] = None,
    category_id: Optional[uuid.UUID] = None,
    priority: Optional[str] = None,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
    current_user: User = Depends(require_role(["super_admin", "state_authority", "district_officer", "agency", "field_officer"])),
    db: AsyncSession = Depends(get_db),
):
    query = select(Project).where(Project.is_deleted == False)
    count_query = select(func.count(Project.id)).where(Project.is_deleted == False)

    # Role-based filtering
    if current_user.role.name == "state_authority":
        query = query.where(Project.state_id == current_user.state_id)
        count_query = count_query.where(Project.state_id == current_user.state_id)
    elif current_user.role.name == "district_officer":
        query = query.where(Project.district_id == current_user.district_id)
        count_query = count_query.where(Project.district_id == current_user.district_id)
    elif current_user.role.name == "agency":
        query = query.where(Project.implementing_agency_id == current_user.id)
        count_query = count_query.where(Project.implementing_agency_id == current_user.id)

    if search:
        search_filter = or_(Project.name.ilike(f"%{search}%"), Project.description.ilike(f"%{search}%"))
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    if status_filter:
        query = query.where(Project.status == status_filter)
        count_query = count_query.where(Project.status == status_filter)
    if state_id:
        query = query.where(Project.state_id == state_id)
        count_query = count_query.where(Project.state_id == state_id)
    if district_id:
        query = query.where(Project.district_id == district_id)
        count_query = count_query.where(Project.district_id == district_id)
    if category_id:
        query = query.where(Project.category_id == category_id)
        count_query = count_query.where(Project.category_id == category_id)
    if priority:
        query = query.where(Project.priority == priority)
        count_query = count_query.where(Project.priority == priority)

    # Sort
    sort_col = getattr(Project, sort_by, Project.created_at)
    if sort_dir == "asc":
        query = query.order_by(sort_col.asc())
    else:
        query = query.order_by(sort_col.desc())

    # Count
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.options(
        selectinload(Project.ministry),
        selectinload(Project.category),
        selectinload(Project.state),
        selectinload(Project.district),
    )
    result = await db.execute(query)
    projects = result.scalars().all()

    items = [project_to_response(p) for p in projects]
    return PaginatedProjects(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(require_role(["super_admin", "state_authority", "agency"])),
    db: AsyncSession = Depends(get_db),
):
    project = Project(
        name=project_data.name,
        ministry_id=project_data.ministry_id,
        category_id=project_data.category_id,
        implementing_agency_id=project_data.implementing_agency_id,
        state_id=project_data.state_id,
        district_id=project_data.district_id,
        description=project_data.description,
        estimated_budget=project_data.estimated_budget,
        estimated_land_required_hectares=project_data.estimated_land_required_hectares,
        priority=project_data.priority,
        start_date=project_data.start_date,
        target_completion_date=project_data.target_completion_date,
        created_by=current_user.id,
    )
    db.add(project)
    await db.flush()

    # Audit log
    audit = AuditLog(
        entity_type="project", entity_id=project.id, action="created",
        performed_by=current_user.id, new_value={"name": project.name, "status": "draft"},
        remarks="Project created"
    )
    db.add(audit)
    await db.commit()
    await db.refresh(project)

    return project_to_response(project)


@router.get("/ministries", response_model=list[MinistryResponse])
async def list_ministries(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ministry))
    return result.scalars().all()


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProjectCategory))
    return result.scalars().all()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.is_deleted == False).options(
            selectinload(Project.ministry),
            selectinload(Project.category),
            selectinload(Project.state),
            selectinload(Project.district),
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_to_response(project)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    update_data: ProjectUpdate,
    current_user: User = Depends(require_role(["super_admin", "state_authority", "agency"])),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.is_deleted == False)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    old_values = {k: str(getattr(project, k)) for k in update_data.model_fields if getattr(project, k, None) is not None}

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(project, key, value)

    # Audit log
    audit = AuditLog(
        entity_type="project", entity_id=project.id, action="updated",
        performed_by=current_user.id, old_value=old_values, new_value=update_dict,
        remarks="Project updated"
    )
    db.add(audit)
    await db.commit()
    await db.refresh(project)
    return project_to_response(project)


@router.delete("/{project_id}")
async def delete_project(
    project_id: uuid.UUID,
    current_user: User = Depends(require_role(["super_admin"])),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project.is_deleted = True
    audit = AuditLog(
        entity_type="project", entity_id=project.id, action="deleted",
        performed_by=current_user.id, remarks="Project soft-deleted"
    )
    db.add(audit)
    await db.commit()
    return {"message": "Project deleted"}


@router.get("/{project_id}/milestones", response_model=list[MilestoneResponse])
async def list_milestones(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Milestone).where(Milestone.project_id == project_id).order_by(Milestone.created_at)
    )
    return result.scalars().all()


@router.post("/{project_id}/milestones", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
async def create_milestone(
    project_id: uuid.UUID,
    data: MilestoneCreate,
    current_user: User = Depends(require_role(["super_admin", "state_authority", "district_officer", "agency"])),
    db: AsyncSession = Depends(get_db),
):
    milestone = Milestone(
        project_id=project_id,
        stage=data.stage,
        title=data.title,
        planned_date=data.planned_date,
        status=data.status,
        responsible_officer_id=data.responsible_officer_id,
        remarks=data.remarks,
    )
    db.add(milestone)
    await db.commit()
    await db.refresh(milestone)
    return milestone


@router.patch("/{project_id}/milestones/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    project_id: uuid.UUID,
    milestone_id: uuid.UUID,
    data: MilestoneUpdate,
    current_user: User = Depends(require_role(["super_admin", "state_authority", "district_officer", "agency"])),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Milestone).where(Milestone.id == milestone_id, Milestone.project_id == project_id)
    )
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(milestone, key, value)

    await db.commit()
    await db.refresh(milestone)
    return milestone


@router.get("/{project_id}/timeline")
async def get_project_timeline(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Get all audit logs for this project
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.entity_type == "project", AuditLog.entity_id == project_id)
        .order_by(AuditLog.created_at)
    )
    logs = result.scalars().all()

    # Get milestones
    ms_result = await db.execute(
        select(Milestone).where(Milestone.project_id == project_id).order_by(Milestone.created_at)
    )
    milestones = ms_result.scalars().all()

    timeline = []
    for log in logs:
        timeline.append({
            "id": str(log.id),
            "type": "audit",
            "action": log.action,
            "old_value": log.old_value,
            "new_value": log.new_value,
            "remarks": log.remarks,
            "performed_by": str(log.performed_by) if log.performed_by else None,
            "timestamp": log.created_at.isoformat() if log.created_at else None,
        })
    for ms in milestones:
        timeline.append({
            "id": str(ms.id),
            "type": "milestone",
            "stage": ms.stage,
            "title": ms.title,
            "status": ms.status.value if hasattr(ms.status, 'value') else str(ms.status),
            "planned_date": ms.planned_date.isoformat() if ms.planned_date else None,
            "actual_date": ms.actual_date.isoformat() if ms.actual_date else None,
            "remarks": ms.remarks,
            "timestamp": ms.created_at.isoformat() if ms.created_at else None,
        })

    timeline.sort(key=lambda x: x.get("timestamp") or "")
    return {"timeline": timeline, "stages": STAGES}
