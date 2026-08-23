from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import uuid

from app.db.session import get_db
from app.models.legal import Objection
from app.models.user import User
from app.core.deps import require_role, get_current_user
from app.schemas.notification import (
    ObjectionCreate,
    ObjectionUpdate,
    ObjectionResponse,
    PaginatedObjections,
)

router = APIRouter(prefix="/objections", tags=["objections"])


@router.get("", response_model=PaginatedObjections)
async def list_objections(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    parcel_id: Optional[uuid.UUID] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Objection)
    count_query = select(func.count(Objection.id))

    if parcel_id:
        query = query.where(Objection.parcel_id == parcel_id)
        count_query = count_query.where(Objection.parcel_id == parcel_id)
    if status_filter:
        query = query.where(Objection.status == status_filter)
        count_query = count_query.where(Objection.status == status_filter)

    total = (await db.execute(count_query)).scalar()
    query = (
        query.order_by(Objection.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedObjections(
        items=[ObjectionResponse.model_validate(o) for o in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=ObjectionResponse, status_code=status.HTTP_201_CREATED)
async def create_objection(
    data: ObjectionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    objection = Objection(**data.model_dump())
    db.add(objection)
    await db.commit()
    await db.refresh(objection)
    return ObjectionResponse.model_validate(objection)


@router.patch("/{objection_id}", response_model=ObjectionResponse)
async def update_objection(
    objection_id: uuid.UUID,
    data: ObjectionUpdate,
    current_user: User = Depends(
        require_role(["super_admin", "state_authority", "district_officer"])
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Objection).where(Objection.id == objection_id))
    objection = result.scalar_one_or_none()
    if not objection:
        raise HTTPException(status_code=404, detail="Objection not found")

    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(objection, key, value)

    await db.commit()
    await db.refresh(objection)
    return ObjectionResponse.model_validate(objection)
