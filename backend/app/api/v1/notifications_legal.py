from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import uuid

from app.db.session import get_db
from app.models.legal import LegalNotification
from app.models.user import User
from app.core.deps import require_role, get_current_user
from app.schemas.notification import (
    LegalNotificationCreate,
    LegalNotificationUpdate,
    LegalNotificationResponse,
    PaginatedLegalNotifications,
)

router = APIRouter(prefix="/notifications-legal", tags=["legal-notifications"])


@router.get("", response_model=PaginatedLegalNotifications)
async def list_legal_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    project_id: Optional[uuid.UUID] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    section_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(LegalNotification)
    count_query = select(func.count(LegalNotification.id))

    if project_id:
        query = query.where(LegalNotification.project_id == project_id)
        count_query = count_query.where(LegalNotification.project_id == project_id)
    if status_filter:
        query = query.where(LegalNotification.status == status_filter)
        count_query = count_query.where(LegalNotification.status == status_filter)
    if section_type:
        query = query.where(LegalNotification.section_type == section_type)
        count_query = count_query.where(LegalNotification.section_type == section_type)

    total = (await db.execute(count_query)).scalar()
    query = (
        query.order_by(LegalNotification.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedLegalNotifications(
        items=[LegalNotificationResponse.model_validate(ln) for ln in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=LegalNotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_legal_notification(
    data: LegalNotificationCreate,
    current_user: User = Depends(
        require_role(["super_admin", "state_authority", "district_officer"])
    ),
    db: AsyncSession = Depends(get_db),
):
    ln = LegalNotification(**data.model_dump())
    db.add(ln)
    await db.commit()
    await db.refresh(ln)
    return LegalNotificationResponse.model_validate(ln)


@router.patch("/{notification_id}", response_model=LegalNotificationResponse)
async def update_legal_notification(
    notification_id: uuid.UUID,
    data: LegalNotificationUpdate,
    current_user: User = Depends(
        require_role(["super_admin", "state_authority", "district_officer"])
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LegalNotification).where(LegalNotification.id == notification_id)
    )
    ln = result.scalar_one_or_none()
    if not ln:
        raise HTTPException(status_code=404, detail="Legal notification not found")

    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(ln, key, value)

    await db.commit()
    await db.refresh(ln)
    return LegalNotificationResponse.model_validate(ln)
