"""Dataset browser API — returns paginated raw data for all core entities."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.db.session import get_db
from app.models.user import User, Role
from app.models.project import Project, Ministry, ProjectCategory
from app.models.state import State, District, Village
from app.models.land import LandParcel, LandOwner
from app.models.compensation import Compensation, Payment
from app.models.document import Document
from app.models.rr import RehabilitationFamily
from app.core.deps import get_current_user

router = APIRouter(prefix="/datasets", tags=["datasets"])

VALID_TABLES = {
    "projects": Project,
    "parcels": LandParcel,
    "users": User,
    "compensations": Compensation,
    "payments": Payment,
    "states": State,
    "districts": District,
    "villages": Village,
    "ministries": Ministry,
    "categories": ProjectCategory,
    "documents": Document,
    "land_owners": LandOwner,
    "rr_families": RehabilitationFamily,
    "roles": Role,
}


def serialize_project(p: Project) -> dict:
    return {
        "id": str(p.id),
        "name": p.name,
        "status": p.status.value if hasattr(p.status, "value") else str(p.status),
        "priority": p.priority.value if hasattr(p.priority, "value") else str(p.priority),
        "current_stage": p.current_stage,
        "estimated_budget": float(p.estimated_budget) if p.estimated_budget else None,
        "estimated_land_required_hectares": float(p.estimated_land_required_hectares)
        if p.estimated_land_required_hectares
        else None,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }


def serialize_parcel(p: LandParcel) -> dict:
    return {
        "id": str(p.id),
        "survey_number": p.survey_number,
        "area_hectares": float(p.area_hectares) if p.area_hectares else None,
        "land_type": p.land_type.value if hasattr(p.land_type, "value") else str(p.land_type),
        "ownership_status": p.ownership_status.value
        if hasattr(p.ownership_status, "value")
        else str(p.ownership_status),
        "verification_status": p.verification_status.value
        if hasattr(p.verification_status, "value")
        else str(p.verification_status),
        "has_geometry": bool(p.geom),
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


def serialize_user(u: User) -> dict:
    return {
        "id": str(u.id),
        "full_name": u.full_name,
        "email": u.email,
        "phone": u.phone,
        "role": u.role.name if u.role else None,
        "is_active": u.is_active,
        "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


def serialize_compensation(c: Compensation) -> dict:
    return {
        "id": str(c.id),
        "parcel_id": str(c.parcel_id),
        "market_value": float(c.market_value) if c.market_value else None,
        "solatium": float(c.solatium) if c.solatium else None,
        "additional_compensation": float(c.additional_compensation)
        if c.additional_compensation
        else None,
        "total_award": float(c.total_award) if c.total_award else None,
        "status": c.status,
        "assessment_date": c.assessment_date.isoformat() if c.assessment_date else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


def serialize_payment(p: Payment) -> dict:
    return {
        "id": str(p.id),
        "compensation_id": str(p.compensation_id),
        "amount": float(p.amount),
        "pfms_reference": p.pfms_reference,
        "payment_status": p.payment_status,
        "bank_verification_status": p.bank_verification_status,
        "disbursed_date": p.disbursed_date.isoformat() if p.disbursed_date else None,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


def serialize_state(s: State) -> dict:
    return {"id": str(s.id), "name": s.name, "code": s.code, "region": s.region}


def serialize_district(d: District) -> dict:
    return {"id": str(d.id), "name": d.name, "code": d.code, "state_id": str(d.state_id)}


def serialize_village(v: Village) -> dict:
    return {"id": str(v.id), "name": v.name, "tehsil": v.tehsil, "district_id": str(v.district_id)}


def serialize_ministry(m: Ministry) -> dict:
    return {"id": str(m.id), "name": m.name, "code": m.code}


def serialize_category(c: ProjectCategory) -> dict:
    return {"id": str(c.id), "name": c.name}


def serialize_document(d: Document) -> dict:
    return {
        "id": str(d.id),
        "file_name": d.file_name,
        "doc_type": d.doc_type.value if hasattr(d.doc_type, "value") else str(d.doc_type),
        "file_size": d.file_size,
        "mime_type": d.mime_type,
        "version": d.version,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }


def serialize_land_owner(lo: LandOwner) -> dict:
    return {
        "id": str(lo.id),
        "full_name": lo.full_name,
        "phone": lo.phone,
        "email": lo.email,
        "share_percentage": float(lo.share_percentage) if lo.share_percentage else None,
        "parcel_id": str(lo.parcel_id),
    }


def serialize_rr_family(f: RehabilitationFamily) -> dict:
    return {
        "id": str(f.id),
        "family_head_name": f.family_head_name,
        "member_count": f.member_count,
        "displaced_status": f.displaced_status,
        "current_stage": f.current_stage,
        "progress_percentage": f.progress_percentage,
        "monetary_benefit_amount": float(f.monetary_benefit_amount)
        if f.monetary_benefit_amount
        else None,
        "created_at": f.created_at.isoformat() if f.created_at else None,
    }


def serialize_role(r: Role) -> dict:
    return {"id": str(r.id), "name": r.name, "description": r.description}


SERIALIZERS = {
    "projects": serialize_project,
    "parcels": serialize_parcel,
    "users": serialize_user,
    "compensations": serialize_compensation,
    "payments": serialize_payment,
    "states": serialize_state,
    "districts": serialize_district,
    "villages": serialize_village,
    "ministries": serialize_ministry,
    "categories": serialize_category,
    "documents": serialize_document,
    "land_owners": serialize_land_owner,
    "rr_families": serialize_rr_family,
    "roles": serialize_role,
}


@router.get("")
async def list_datasets(
    table: str = Query(..., description="Table name to browse"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if table not in VALID_TABLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid table: {table}. Valid: {list(VALID_TABLES.keys())}",
        )

    model = VALID_TABLES[table]
    serializer = SERIALIZERS[table]

    query = select(model)
    count_query = select(func.count(model.id))

    # Search on text fields
    if search and table == "projects":
        query = query.where(Project.name.ilike(f"%{search}%"))
        count_query = count_query.where(Project.name.ilike(f"%{search}%"))
    elif search and table == "users":
        query = query.where(User.full_name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%"))
        count_query = count_query.where(
            User.full_name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%")
        )
    elif search and table == "parcels":
        query = query.where(LandParcel.survey_number.ilike(f"%{search}%"))
        count_query = count_query.where(LandParcel.survey_number.ilike(f"%{search}%"))

    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(model.id).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": [serializer(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
        "table": table,
        "available_tables": list(VALID_TABLES.keys()),
    }


@router.get("/summary")
async def dataset_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get row counts for all tables — used by the dataset page overview."""
    summaries = {}
    for name, model in VALID_TABLES.items():
        count = (await db.execute(select(func.count(model.id)))).scalar() or 0
        summaries[name] = count
    return {"tables": summaries}
