from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid

from app.db.session import get_db
from app.models.project import (
    Project,
    Milestone,
    Ministry,
    ProjectCategory,
)
from app.models.user import User
from app.core.deps import require_role, get_current_user
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    MilestoneCreate,
    MilestoneUpdate,
    MinistryResponse,
    CategoryResponse,
)
from app.services.project_service import (
    list_projects,
    create_project,
    get_project_by_id,
    update_project,
    soft_delete_project,
    get_project_timeline,
)
from sqlalchemy import select

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("")
async def list_projects_endpoint(
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
    current_user: User = Depends(
        require_role(
            ["super_admin", "state_authority", "district_officer", "agency", "field_officer"]
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    return await list_projects(
        db,
        current_user,
        page,
        page_size,
        search,
        status_filter,
        state_id,
        district_id,
        category_id,
        priority,
        sort_by,
        sort_dir,
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project_endpoint(
    project_data: ProjectCreate,
    current_user: User = Depends(require_role(["super_admin", "state_authority", "agency"])),
    db: AsyncSession = Depends(get_db),
):
    return await create_project(db, project_data, current_user.id)


@router.get("/ministries", response_model=list[MinistryResponse])
async def list_ministries(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ministry))
    return result.scalars().all()


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProjectCategory))
    return result.scalars().all()


@router.get("/{project_id}")
async def get_project_endpoint(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await get_project_by_id(db, project_id)
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    return result


@router.patch("/{project_id}")
async def update_project_endpoint(
    project_id: uuid.UUID,
    update_data: ProjectUpdate,
    current_user: User = Depends(require_role(["super_admin", "state_authority", "agency"])),
    db: AsyncSession = Depends(get_db),
):
    result = await update_project(db, project_id, update_data, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Project not found")
    return result


@router.delete("/{project_id}")
async def delete_project_endpoint(
    project_id: uuid.UUID,
    current_user: User = Depends(require_role(["super_admin"])),
    db: AsyncSession = Depends(get_db),
):
    success = await soft_delete_project(db, project_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted"}


@router.get("/{project_id}/milestones")
async def list_milestones(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Milestone).where(Milestone.project_id == project_id).order_by(Milestone.created_at)
    )
    return result.scalars().all()


@router.post("/{project_id}/milestones", status_code=status.HTTP_201_CREATED)
async def create_milestone(
    project_id: uuid.UUID,
    data: MilestoneCreate,
    current_user: User = Depends(
        require_role(["super_admin", "state_authority", "district_officer", "agency"])
    ),
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


@router.patch("/{project_id}/milestones/{milestone_id}")
async def update_milestone(
    project_id: uuid.UUID,
    milestone_id: uuid.UUID,
    data: MilestoneUpdate,
    current_user: User = Depends(
        require_role(["super_admin", "state_authority", "district_officer", "agency"])
    ),
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
async def get_project_timeline_endpoint(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_project_timeline(db, project_id)
