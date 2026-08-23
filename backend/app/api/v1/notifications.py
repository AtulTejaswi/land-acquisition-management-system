from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime, timezone
import uuid

from app.db.session import get_db
from app.models.notification import NotificationApp
from app.models.legal import LegalNotification, Objection
from app.models.user import User
from app.core.deps import require_role, get_current_user
from app.schemas.notification import (
    NotificationResponse, PaginatedNotifications,
    LegalNotificationCreate, LegalNotificationResponse,
    ObjectionCreate, ObjectionUpdate, ObjectionResponse,
)

router = APIRouter(tags=["notifications"])


# ===== In-App Notifications =====
@router.get("/notifications", response_model=PaginatedNotifications)
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_read: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(NotificationApp).where(NotificationApp.user_id == current_user.id)
    count_query = select(func.count(NotificationApp.id)).where(NotificationApp.user_id == current_user.id)

    if is_read is not None:
        query = query.where(NotificationApp.is_read == is_read)
        count_query = count_query.where(NotificationApp.is_read == is_read)

    total = (await db.execute(count_query)).scalar()
    query = query.order_by(NotificationApp.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedNotifications(
        items=[NotificationResponse.model_validate(n) for n in items],
        total=total, page=page, page_size=page_size,
    )


@router.patch("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(NotificationApp).where(
            NotificationApp.id == notification_id,
            NotificationApp.user_id == current_user.id,
        )
    )
    notif = result.scalar_one_or_none()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    await db.commit()
    return {"message": "Marked as read"}


# ===== Legal Notifications =====
@router.get("/notifications-legal", response_model=list[LegalNotificationResponse])
async def list_legal_notifications(
    project_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(LegalNotification)
    if project_id:
        query = query.where(LegalNotification.project_id == project_id)
    result = await db.execute(query.order_by(LegalNotification.created_at.desc()))
    return [LegalNotificationResponse.model_validate(ln) for ln in result.scalars().all()]


@router.post("/notifications-legal", response_model=LegalNotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_legal_notification(
    data: LegalNotificationCreate,
    current_user: User = Depends(require_role(["super_admin", "state_authority", "district_officer"])),
    db: AsyncSession = Depends(get_db),
):
    ln = LegalNotification(**data.model_dump())
    db.add(ln)
    await db.commit()
    await db.refresh(ln)
    return LegalNotificationResponse.model_validate(ln)


# ===== Objections =====
@router.get("/objections", response_model=list[ObjectionResponse])
async def list_objections(
    parcel_id: Optional[uuid.UUID] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Objection)
    if parcel_id:
        query = query.where(Objection.parcel_id == parcel_id)
    if status_filter:
        query = query.where(Objection.status == status_filter)
    result = await db.execute(query.order_by(Objection.created_at.desc()))
    return [ObjectionResponse.model_validate(o) for o in result.scalars().all()]


@router.post("/objections", response_model=ObjectionResponse, status_code=status.HTTP_201_CREATED)
async def create_objection(
    data: ObjectionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    objection = Objection(
        **data.model_dump(),
        filed_by=current_user.id,
    )
    db.add(objection)
    await db.commit()
    await db.refresh(objection)
    return ObjectionResponse.model_validate(objection)


@router.patch("/objections/{objection_id}", response_model=ObjectionResponse)
async def update_objection(
    objection_id: uuid.UUID,
    data: ObjectionUpdate,
    current_user: User = Depends(require_role(["super_admin", "state_authority", "district_officer"])),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Objection).where(Objection.id == objection_id))
    objection = result.scalar_one_or_none()
    if not objection:
        raise HTTPException(status_code=404, detail="Objection not found")

    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(objection, key, value)
    if data.status in ("resolved", "rejected"):
        objection.resolved_by = current_user.id
    await db.commit()
    await db.refresh(objection)
    return ObjectionResponse.model_validate(objection)
