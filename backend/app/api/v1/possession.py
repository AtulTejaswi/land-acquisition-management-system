from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import uuid
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.possession import Possession
from app.models.land import LandParcel
from app.models.project import Project
from app.models.user import User
from app.models.audit import AuditLog
from app.core.deps import require_role, get_current_user
from app.schemas.possession import PossessionCreate, PossessionResponse

router = APIRouter(prefix="/possession", tags=["possession"])


@router.get("", response_model=list[PossessionResponse])
async def list_possessions(
    parcel_id: Optional[uuid.UUID] = None,
    project_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Possession)
    if parcel_id:
        query = query.where(Possession.parcel_id == parcel_id)
    if project_id:
        query = query.join(LandParcel, Possession.parcel_id == LandParcel.id).where(
            LandParcel.project_id == project_id
        )
    result = await db.execute(query.order_by(Possession.created_at.desc()))
    return [PossessionResponse.model_validate(p) for p in result.scalars().all()]


@router.get("/{possession_id}", response_model=PossessionResponse)
async def get_possession(
    possession_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Possession).where(Possession.id == possession_id))
    pos = result.scalar_one_or_none()
    if not pos:
        raise HTTPException(status_code=404, detail="Possession record not found")
    return PossessionResponse.model_validate(pos)


@router.post("", response_model=PossessionResponse, status_code=status.HTTP_201_CREATED)
async def create_possession(
    data: PossessionCreate,
    current_user: User = Depends(
        require_role(["super_admin", "state_authority", "district_officer"])
    ),
    db: AsyncSession = Depends(get_db),
):
    pos = Possession(
        parcel_id=data.parcel_id,
        possession_date=data.possession_date or datetime.now(timezone.utc),
        taken_by=current_user.id,
        possession_type=data.possession_type,
        remarks=data.remarks,
        document_id=data.document_id if hasattr(data, "document_id") else None,
    )
    db.add(pos)
    await db.flush()

    # Audit log
    audit = AuditLog(
        entity_type="possession",
        entity_id=pos.id,
        action="create",
        performed_by=current_user.id,
        new_value={
            "parcel_id": str(data.parcel_id),
            "possession_type": data.possession_type,
            "remarks": data.remarks,
        },
        remarks="Physical possession recorded",
    )
    db.add(audit)
    await db.commit()
    await db.refresh(pos)
    return PossessionResponse.model_validate(pos)


@router.get("/project/{project_id}/status")
async def get_project_possession_status(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get possession completion percentage and status per parcel for a project."""
    # Get all parcels for this project
    parcels_result = await db.execute(
        select(LandParcel).where(
            LandParcel.project_id == project_id, LandParcel.is_deleted == False
        )
    )
    parcels = parcels_result.scalars().all()

    if not parcels:
        return {
            "project_id": str(project_id),
            "total_parcels": 0,
            "possessed_parcels": 0,
            "completion_percentage": 0,
            "parcels": [],
        }

    parcel_ids = [p.id for p in parcels]

    # Get possession records for these parcels
    pos_result = await db.execute(select(Possession).where(Possession.parcel_id.in_(parcel_ids)))
    possessions = pos_result.scalars().all()
    possessed_parcel_ids = {p.parcel_id for p in possessions}

    parcel_details = []
    for p in parcels:
        has_possession = p.id in possessed_parcel_ids
        pos_record = next((po for po in possessions if po.parcel_id == p.id), None)
        parcel_details.append(
            {
                "parcel_id": str(p.id),
                "survey_number": p.survey_number,
                "area_hectares": float(p.area_hectares) if p.area_hectares else 0,
                "has_possession": has_possession,
                "possession_id": str(pos_record.id) if pos_record else None,
                "possession_date": (
                    pos_record.possession_date.isoformat()
                    if pos_record and pos_record.possession_date
                    else None
                ),
                "possession_type": pos_record.possession_type if pos_record else None,
                "remarks": pos_record.remarks if pos_record else None,
            }
        )

    total = len(parcels)
    possessed = len(possessed_parcel_ids)

    return {
        "project_id": str(project_id),
        "total_parcels": total,
        "possessed_parcels": possessed,
        "completion_percentage": round((possessed / total * 100) if total > 0 else 0, 1),
        "parcels": parcel_details,
    }
