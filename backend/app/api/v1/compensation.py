from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime, timezone
import uuid
import random
import string

from app.db.session import get_db
from app.models.compensation import Compensation, Payment
from app.models.land import LandParcel
from app.models.possession import Possession
from app.models.rr import RehabilitationFamily
from app.models.user import User
from app.core.deps import require_role, get_current_user
from app.schemas.compensation import (
    CompensationCreate, CompensationUpdate, CompensationResponse, PaginatedCompensations,
    PaymentCreate, PaymentUpdate, PaymentResponse, PaginatedPayments,
    RRFamilyCreate, RRFamilyUpdate, RRFamilyResponse, PaginatedRRFamilies,
)
from app.schemas.possession import PossessionCreate, PossessionResponse

router = APIRouter(tags=["compensation"])


def generate_pfms_reference():
    return "PFMS-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=12))


# ===== Compensation =====
@router.get("/compensation", response_model=PaginatedCompensations)
async def list_compensations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    parcel_id: Optional[uuid.UUID] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Compensation)
    count_query = select(func.count(Compensation.id))

    if parcel_id:
        query = query.where(Compensation.parcel_id == parcel_id)
        count_query = count_query.where(Compensation.parcel_id == parcel_id)
    if status_filter:
        query = query.where(Compensation.status == status_filter)
        count_query = count_query.where(Compensation.status == status_filter)

    total = (await db.execute(count_query)).scalar()
    query = query.order_by(Compensation.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()
    return PaginatedCompensations(
        items=[CompensationResponse.model_validate(c) for c in items],
        total=total, page=page, page_size=page_size,
    )


@router.post("/compensation", response_model=CompensationResponse, status_code=status.HTTP_201_CREATED)
async def create_compensation(
    data: CompensationCreate,
    current_user: User = Depends(require_role(["super_admin", "state_authority", "district_officer"])),
    db: AsyncSession = Depends(get_db),
):
    solatium = data.solatium or (data.market_value * 1.0 if data.market_value else 0)
    total = (data.market_value or 0) + solatium + (data.additional_compensation or 0)

    comp = Compensation(
        parcel_id=data.parcel_id,
        market_value=data.market_value,
        solatium=solatium,
        additional_compensation=data.additional_compensation,
        total_award=total,
        assessed_by=current_user.id,
        assessment_date=datetime.now(timezone.utc),
    )
    db.add(comp)
    await db.commit()
    await db.refresh(comp)
    return CompensationResponse.model_validate(comp)


@router.patch("/compensation/{comp_id}", response_model=CompensationResponse)
async def update_compensation(
    comp_id: uuid.UUID,
    data: CompensationUpdate,
    current_user: User = Depends(require_role(["super_admin", "state_authority", "district_officer"])),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Compensation).where(Compensation.id == comp_id))
    comp = result.scalar_one_or_none()
    if not comp:
        raise HTTPException(status_code=404, detail="Compensation not found")

    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(comp, key, value)

    # Recalculate total
    comp.total_award = (comp.market_value or 0) + (comp.solatium or 0) + (comp.additional_compensation or 0)
    await db.commit()
    await db.refresh(comp)
    return CompensationResponse.model_validate(comp)


# ===== Payments =====
@router.get("/payments", response_model=PaginatedPayments)
async def list_payments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    compensation_id: Optional[uuid.UUID] = None,
    payment_status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Payment)
    count_query = select(func.count(Payment.id))

    if compensation_id:
        query = query.where(Payment.compensation_id == compensation_id)
        count_query = count_query.where(Payment.compensation_id == compensation_id)
    if payment_status:
        query = query.where(Payment.payment_status == payment_status)
        count_query = count_query.where(Payment.payment_status == payment_status)

    total = (await db.execute(count_query)).scalar()
    query = query.order_by(Payment.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()
    return PaginatedPayments(
        items=[PaymentResponse.model_validate(p) for p in items],
        total=total, page=page, page_size=page_size,
    )


@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    data: PaymentCreate,
    current_user: User = Depends(require_role(["super_admin", "state_authority", "district_officer"])),
    db: AsyncSession = Depends(get_db),
):
    payment = Payment(
        compensation_id=data.compensation_id,
        land_owner_id=data.land_owner_id,
        amount=data.amount,
        pfms_reference=generate_pfms_reference(),
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return PaymentResponse.model_validate(payment)


@router.patch("/payments/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: uuid.UUID,
    data: PaymentUpdate,
    current_user: User = Depends(require_role(["super_admin", "state_authority", "district_officer"])),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(payment, key, value)
    await db.commit()
    await db.refresh(payment)
    return PaymentResponse.model_validate(payment)


# ===== Possession =====
@router.get("/possession", response_model=list[PossessionResponse])
async def list_possessions(
    parcel_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Possession)
    if parcel_id:
        query = query.where(Possession.parcel_id == parcel_id)
    result = await db.execute(query.order_by(Possession.created_at.desc()))
    return [PossessionResponse.model_validate(p) for p in result.scalars().all()]


@router.post("/possession", response_model=PossessionResponse, status_code=status.HTTP_201_CREATED)
async def create_possession(
    data: PossessionCreate,
    current_user: User = Depends(require_role(["super_admin", "state_authority", "district_officer"])),
    db: AsyncSession = Depends(get_db),
):
    pos = Possession(
        parcel_id=data.parcel_id,
        possession_date=data.possession_date,
        taken_by=current_user.id,
        possession_type=data.possession_type,
        remarks=data.remarks,
    )
    db.add(pos)
    await db.commit()
    await db.refresh(pos)
    return PossessionResponse.model_validate(pos)


# ===== R&R Families =====
@router.get("/rr/families", response_model=PaginatedRRFamilies)
async def list_rr_families(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    project_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(RehabilitationFamily)
    count_query = select(func.count(RehabilitationFamily.id))

    if project_id:
        query = query.where(RehabilitationFamily.project_id == project_id)
        count_query = count_query.where(RehabilitationFamily.project_id == project_id)

    total = (await db.execute(count_query)).scalar()
    query = query.order_by(RehabilitationFamily.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()
    return PaginatedRRFamilies(
        items=[RRFamilyResponse.model_validate(f) for f in items],
        total=total, page=page, page_size=page_size,
    )


@router.post("/rr/families", response_model=RRFamilyResponse, status_code=status.HTTP_201_CREATED)
async def create_rr_family(
    data: RRFamilyCreate,
    current_user: User = Depends(require_role(["super_admin", "state_authority", "district_officer"])),
    db: AsyncSession = Depends(get_db),
):
    family = RehabilitationFamily(**data.model_dump())
    db.add(family)
    await db.commit()
    await db.refresh(family)
    return RRFamilyResponse.model_validate(family)


@router.patch("/rr/families/{family_id}", response_model=RRFamilyResponse)
async def update_rr_family(
    family_id: uuid.UUID,
    data: RRFamilyUpdate,
    current_user: User = Depends(require_role(["super_admin", "state_authority", "district_officer"])),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(RehabilitationFamily).where(RehabilitationFamily.id == family_id))
    family = result.scalar_one_or_none()
    if not family:
        raise HTTPException(status_code=404, detail="RR Family not found")

    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(family, key, value)
    await db.commit()
    await db.refresh(family)
    return RRFamilyResponse.model_validate(family)
