from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import Optional
import uuid

from app.models.project import (
    Project,
    Milestone,
    Ministry,
    ProjectCategory,
    STAGES,
)
from app.models.audit import AuditLog
from app.schemas.project import (
    ProjectResponse,
    ProjectCreate,
    ProjectUpdate,
    PaginatedProjects,
)


def project_to_response(p: Project) -> ProjectResponse:
    return ProjectResponse(
        id=p.id,
        name=p.name,
        ministry_id=p.ministry_id,
        category_id=p.category_id,
        implementing_agency_id=p.implementing_agency_id,
        state_id=p.state_id,
        district_id=p.district_id,
        description=p.description,
        estimated_budget=float(p.estimated_budget) if p.estimated_budget else None,
        estimated_land_required_hectares=float(p.estimated_land_required_hectares)
        if p.estimated_land_required_hectares
        else None,
        priority=p.priority.value if hasattr(p.priority, "value") else str(p.priority),
        current_stage=p.current_stage,
        status=p.status.value if hasattr(p.status, "value") else str(p.status),
        start_date=p.start_date,
        target_completion_date=p.target_completion_date,
        created_by=p.created_by,
        created_at=p.created_at,
        updated_at=p.updated_at,
        ministry_name=p.ministry.name if p.ministry else None,
        category_name=p.category.name if p.category else None,
        state_name=p.state.name if p.state else None,
        district_name=p.district.name if p.district else None,
        created_by_name=p.creator.full_name if hasattr(p, "creator") and p.creator else None,
    )


async def list_projects(
    db: AsyncSession,
    current_user,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    state_id: Optional[uuid.UUID] = None,
    district_id: Optional[uuid.UUID] = None,
    category_id: Optional[uuid.UUID] = None,
    priority: Optional[str] = None,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
) -> PaginatedProjects:
    query = select(Project).where(Project.is_deleted == False)
    count_query = select(func.count(Project.id)).where(Project.is_deleted == False)

    # Role-based filtering
    role_name = current_user.role.name if current_user.role else ""
    if role_name == "state_authority":
        query = query.where(Project.state_id == current_user.state_id)
        count_query = count_query.where(Project.state_id == current_user.state_id)
    elif role_name == "district_officer":
        query = query.where(Project.district_id == current_user.district_id)
        count_query = count_query.where(Project.district_id == current_user.district_id)
    elif role_name == "agency":
        query = query.where(Project.implementing_agency_id == current_user.id)
        count_query = count_query.where(Project.implementing_agency_id == current_user.id)

    if search:
        search_filter = or_(
            Project.name.ilike(f"%{search}%"), Project.description.ilike(f"%{search}%")
        )
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

    sort_col = getattr(Project, sort_by, Project.created_at)
    query = query.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())

    total = (await db.execute(count_query)).scalar()

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


async def create_project(
    db: AsyncSession, project_data: ProjectCreate, created_by: uuid.UUID
) -> ProjectResponse:
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
        created_by=created_by,
    )
    db.add(project)
    await db.flush()

    audit = AuditLog(
        entity_type="project",
        entity_id=project.id,
        action="created",
        performed_by=created_by,
        new_value={"name": project.name, "status": "draft"},
        remarks="Project created",
    )
    db.add(audit)
    await db.commit()
    await db.refresh(project)
    return project_to_response(project)


async def get_project_by_id(db: AsyncSession, project_id: uuid.UUID) -> Optional[ProjectResponse]:
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id, Project.is_deleted == False)
        .options(
            selectinload(Project.ministry),
            selectinload(Project.category),
            selectinload(Project.state),
            selectinload(Project.district),
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        return None
    return project_to_response(project)


async def update_project(
    db: AsyncSession,
    project_id: uuid.UUID,
    update_data: ProjectUpdate,
    updated_by: uuid.UUID,
) -> Optional[ProjectResponse]:
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.is_deleted == False)
    )
    project = result.scalar_one_or_none()
    if not project:
        return None

    old_values = {
        k: str(getattr(project, k))
        for k in update_data.model_fields
        if getattr(project, k, None) is not None
    }
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(project, key, value)

    audit = AuditLog(
        entity_type="project",
        entity_id=project.id,
        action="updated",
        performed_by=updated_by,
        old_value=old_values,
        new_value=update_dict,
        remarks="Project updated",
    )
    db.add(audit)
    await db.commit()
    await db.refresh(project)
    return project_to_response(project)


async def soft_delete_project(
    db: AsyncSession, project_id: uuid.UUID, deleted_by: uuid.UUID
) -> bool:
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        return False
    project.is_deleted = True
    audit = AuditLog(
        entity_type="project",
        entity_id=project.id,
        action="deleted",
        performed_by=deleted_by,
        remarks="Project soft-deleted",
    )
    db.add(audit)
    await db.commit()
    return True


async def get_project_timeline(db: AsyncSession, project_id: uuid.UUID) -> dict:
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.entity_type == "project", AuditLog.entity_id == project_id)
        .order_by(AuditLog.created_at)
    )
    logs = result.scalars().all()

    ms_result = await db.execute(
        select(Milestone).where(Milestone.project_id == project_id).order_by(Milestone.created_at)
    )
    milestones = ms_result.scalars().all()

    timeline = []
    for log in logs:
        timeline.append(
            {
                "id": str(log.id),
                "type": "audit",
                "action": log.action,
                "old_value": log.old_value,
                "new_value": log.new_value,
                "remarks": log.remarks,
                "performed_by": str(log.performed_by) if log.performed_by else None,
                "timestamp": log.created_at.isoformat() if log.created_at else None,
            }
        )
    for ms in milestones:
        timeline.append(
            {
                "id": str(ms.id),
                "type": "milestone",
                "stage": ms.stage,
                "title": ms.title,
                "status": ms.status.value if hasattr(ms.status, "value") else str(ms.status),
                "planned_date": ms.planned_date.isoformat() if ms.planned_date else None,
                "actual_date": ms.actual_date.isoformat() if ms.actual_date else None,
                "remarks": ms.remarks,
                "timestamp": ms.created_at.isoformat() if ms.created_at else None,
            }
        )

    timeline.sort(key=lambda x: x.get("timestamp") or "")
    return {"timeline": timeline, "stages": STAGES}
