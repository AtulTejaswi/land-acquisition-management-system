from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import uuid

from app.db.session import get_db
from app.models.user import User, Role
from app.core.deps import require_role
from app.core.security import get_password_hash
from app.schemas.auth import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    role: Optional[str] = None,
    search: Optional[str] = None,
    state_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(require_role(["super_admin"])),
    db: AsyncSession = Depends(get_db),
):
    query = select(User).where(User.is_deleted == False)
    if role:
        query = query.join(Role).where(Role.name == role)
    if search:
        query = query.where(User.full_name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%"))
    if state_id:
        query = query.where(User.state_id == state_id)

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    users = result.scalars().all()

    return [
        UserResponse(
            id=u.id,
            full_name=u.full_name,
            email=u.email,
            phone=u.phone,
            role_name=u.role.name if u.role else "",
            state_id=u.state_id,
            state_name=u.state.name if u.state else None,
            district_id=u.district_id,
            district_name=u.district.name if u.district else None,
            agency_name=u.agency_name,
            is_active=u.is_active,
        )
        for u in users
    ]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    current_user: User = Depends(require_role(["super_admin"])),
    db: AsyncSession = Depends(get_db),
):
    user = User(
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        password_hash=get_password_hash(data.password),
        role_id=data.role_id,
        state_id=data.state_id,
        district_id=data.district_id,
        agency_name=data.agency_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        role_name=user.role.name if user.role else "",
        state_id=user.state_id,
        state_name=user.state.name if user.state else None,
        district_id=user.district_id,
        district_name=user.district.name if user.district else None,
        agency_name=user.agency_name,
        is_active=user.is_active,
    )


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    current_user: User = Depends(require_role(["super_admin"])),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return UserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        role_name=user.role.name if user.role else "",
        state_id=user.state_id,
        district_id=user.district_id,
        agency_name=user.agency_name,
        is_active=user.is_active,
    )
