from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import Optional
import uuid

from app.db.session import get_db
from app.models.land import LandParcel, LandOwner
from app.models.state import Village, District, State
from app.models.user import User
from app.core.deps import require_role, get_current_user
from app.schemas.parcel import (
    ParcelCreate,
    ParcelUpdate,
    ParcelResponse,
    PaginatedParcels,
    LandOwnerCreate,
    LandOwnerResponse,
)

router = APIRouter(prefix="/parcels", tags=["parcels"])


def parcel_to_response(p: LandParcel) -> ParcelResponse:
    return ParcelResponse(
        id=p.id,
        project_id=p.project_id,
        survey_number=p.survey_number,
        village_id=p.village_id,
        district_id=p.district_id,
        state_id=p.state_id,
        area_hectares=float(p.area_hectares) if p.area_hectares else None,
        land_type=p.land_type.value if hasattr(p.land_type, "value") else str(p.land_type),
        ownership_status=p.ownership_status.value
        if hasattr(p.ownership_status, "value")
        else str(p.ownership_status),
        verification_status=p.verification_status.value
        if hasattr(p.verification_status, "value")
        else str(p.verification_status),
        created_at=p.created_at,
        updated_at=p.updated_at,
        village_name=p.village.name if p.village else None,
        district_name=p.district.name if p.district else None,
        state_name=p.state.name if p.state else None,
        owners=[
            LandOwnerResponse(
                id=o.id,
                parcel_id=o.parcel_id,
                full_name=o.full_name,
                aadhaar_masked=o.aadhaar_masked,
                phone=o.phone,
                email=o.email,
                bank_account_masked=o.bank_account_masked,
                ifsc=o.ifsc,
                share_percentage=float(o.share_percentage) if o.share_percentage else None,
                user_id=o.user_id,
            )
            for o in (p.owners if p.owners else [])
        ],
    )


@router.get("", response_model=PaginatedParcels)
async def list_parcels(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    project_id: Optional[uuid.UUID] = None,
    state_id: Optional[uuid.UUID] = None,
    district_id: Optional[uuid.UUID] = None,
    land_type: Optional[str] = None,
    verification_status: Optional[str] = None,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(LandParcel).where(LandParcel.is_deleted == False)
    count_query = select(func.count(LandParcel.id)).where(LandParcel.is_deleted == False)

    if project_id:
        query = query.where(LandParcel.project_id == project_id)
        count_query = count_query.where(LandParcel.project_id == project_id)
    if state_id:
        query = query.where(LandParcel.state_id == state_id)
        count_query = count_query.where(LandParcel.state_id == state_id)
    if district_id:
        query = query.where(LandParcel.district_id == district_id)
        count_query = count_query.where(LandParcel.district_id == district_id)
    if land_type:
        query = query.where(LandParcel.land_type == land_type)
        count_query = count_query.where(LandParcel.land_type == land_type)
    if verification_status:
        query = query.where(LandParcel.verification_status == verification_status)
        count_query = count_query.where(LandParcel.verification_status == verification_status)
    if search:
        search_filter = LandParcel.survey_number.ilike(f"%{search}%")
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    sort_col = getattr(LandParcel, sort_by, LandParcel.created_at)
    query = query.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())

    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = (
        query.options(
            selectinload(LandParcel.village),
            selectinload(LandParcel.district),
            selectinload(LandParcel.state),
            selectinload(LandParcel.owners),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    parcels = result.scalars().unique().all()

    items = [parcel_to_response(p) for p in parcels]
    return PaginatedParcels(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=ParcelResponse, status_code=status.HTTP_201_CREATED)
async def create_parcel(
    data: ParcelCreate,
    current_user: User = Depends(
        require_role(["super_admin", "state_authority", "district_officer", "agency"])
    ),
    db: AsyncSession = Depends(get_db),
):
    parcel = LandParcel(
        project_id=data.project_id,
        survey_number=data.survey_number,
        village_id=data.village_id,
        district_id=data.district_id,
        state_id=data.state_id,
        area_hectares=data.area_hectares,
        geom=data.geom,
        land_type=data.land_type,
        ownership_status=data.ownership_status,
    )
    db.add(parcel)
    await db.commit()
    await db.refresh(parcel)
    return parcel_to_response(parcel)


@router.get("/{parcel_id}", response_model=ParcelResponse)
async def get_parcel(
    parcel_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LandParcel)
        .where(LandParcel.id == parcel_id, LandParcel.is_deleted == False)
        .options(
            selectinload(LandParcel.village),
            selectinload(LandParcel.district),
            selectinload(LandParcel.state),
            selectinload(LandParcel.owners),
        )
    )
    parcel = result.scalar_one_or_none()
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")
    return parcel_to_response(parcel)


@router.patch("/{parcel_id}", response_model=ParcelResponse)
async def update_parcel(
    parcel_id: uuid.UUID,
    data: ParcelUpdate,
    current_user: User = Depends(
        require_role(["super_admin", "state_authority", "district_officer"])
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LandParcel).where(LandParcel.id == parcel_id, LandParcel.is_deleted == False)
    )
    parcel = result.scalar_one_or_none()
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")

    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(parcel, key, value)

    await db.commit()
    await db.refresh(parcel)
    return parcel_to_response(parcel)


@router.get("/{parcel_id}/owners", response_model=list[LandOwnerResponse])
async def list_owners(
    parcel_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(LandOwner).where(LandOwner.parcel_id == parcel_id))
    return result.scalars().all()


@router.post(
    "/{parcel_id}/owners", response_model=LandOwnerResponse, status_code=status.HTTP_201_CREATED
)
async def add_owner(
    parcel_id: uuid.UUID,
    data: LandOwnerCreate,
    current_user: User = Depends(
        require_role(["super_admin", "state_authority", "district_officer"])
    ),
    db: AsyncSession = Depends(get_db),
):
    owner = LandOwner(
        parcel_id=parcel_id,
        full_name=data.full_name,
        aadhaar_masked=data.aadhaar_masked,
        phone=data.phone,
        email=data.email,
        bank_account_masked=data.bank_account_masked,
        ifsc=data.ifsc,
        share_percentage=data.share_percentage,
        user_id=data.user_id,
    )
    db.add(owner)
    await db.commit()
    await db.refresh(owner)
    return owner
