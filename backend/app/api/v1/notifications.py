from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime, timezone
import uuid

from app.db.session import get_db
from app.models.notification import NotificationApp
from app.models.user import User
from app.core.deps import require_role, get_current_user
from app.schemas.notification import (
    NotificationResponse,
    PaginatedNotifications,
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
    count_query = select(func.count(NotificationApp.id)).where(
        NotificationApp.user_id == current_user.id
    )

    if is_read is not None:
        query = query.where(NotificationApp.is_read == is_read)
        count_query = count_query.where(NotificationApp.is_read == is_read)

    total = (await db.execute(count_query)).scalar()
    query = (
        query.order_by(NotificationApp.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedNotifications(
        items=[NotificationResponse.model_validate(n) for n in items],
        total=total,
        page=page,
        page_size=page_size,
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
