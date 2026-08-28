"""ML inference endpoints for the land-nature screening model.

Contract: docs/ml-inference-contract.md. All endpoints require authentication;
predictions are restricted to government-users (staff roles), never citizens,
because screening output is an internal decision-support aid over non-public
record analysis.
"""

import asyncio
import logging
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.deps import require_role
from app.db.session import get_db
from app.ml.normalize import is_compound_survey, survey_number_head
from app.ml.service import DISCLAIMER, ModelUnavailableError, land_nature_model
from app.models.land import LandParcel
from app.models.user import User
from app.schemas.ml import LandNaturePredictRequest, MlHealthResponse, MlPredictionResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ml", tags=["ml-inference"])

STAFF_ROLES = ["super_admin", "state_authority", "district_officer", "agency", "field_officer"]


async def _bounded_predict(**kwargs) -> dict:
    """Run inference in a worker thread with a bounded timeout."""
    return await asyncio.wait_for(
        asyncio.to_thread(land_nature_model.predict, **kwargs),
        timeout=settings.ML_INFERENCE_TIMEOUT_SECONDS,
    )


# ---------------------------------------------------------------------------
# Core ML inference endpoints
# ---------------------------------------------------------------------------


@router.get("/health", response_model=MlHealthResponse)
async def ml_health(current_user: User = Depends(require_role(STAFF_ROLES))):
    status = land_nature_model.status()
    return {"status": status["status"], "model": status}


@router.get("/parcels/{parcel_id}/land-nature", response_model=MlPredictionResponse)
async def parcel_land_nature(
    parcel_id: uuid.UUID,
    current_user: User = Depends(require_role(STAFF_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    from app.models.land import LandOwner

    result = await db.execute(
        select(LandParcel, func.count(LandOwner.id))
        .outerjoin(LandOwner, LandOwner.parcel_id == LandParcel.id)
        .where(LandParcel.id == parcel_id, LandParcel.is_deleted == False)
        .group_by(LandParcel.id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Parcel not found")
    parcel, owner_count = row

    village_name = None
    if parcel.village_id:
        from app.models.state import Village

        village = (await db.execute(select(Village).where(Village.id == parcel.village_id))).scalar_one_or_none()
        village_name = village.name if village else None

    try:
        envelope = await _bounded_predict(
            village=village_name,
            area_hectares=float(parcel.area_hectares) if parcel.area_hectares else None,
            survey_head=survey_number_head(parcel.survey_number),
            is_compound=is_compound_survey(parcel.survey_number),
            party_count=owner_count,
            land_type=parcel.land_type.value if parcel.land_type else None,
            entity_type="parcel",
            entity_id=str(parcel.id),
        )
    except ModelUnavailableError:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "ML model unavailable; no prediction was generated",
                "model": land_nature_model.status(),
                "disclaimer": DISCLAIMER,
            },
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Model inference timed out")

    envelope["explanation"]["factors"].append(
        {"name": "recorded_ownership_status", "value": parcel.ownership_status.value}
    )
    return envelope


@router.post("/land-nature/predict", response_model=MlPredictionResponse)
async def predict_land_nature(
    body: LandNaturePredictRequest,
    current_user: User = Depends(require_role(STAFF_ROLES)),
):
    try:
        envelope = await _bounded_predict(
            village=body.village,
            area_hectares=body.area_hectares,
            survey_head=survey_number_head(body.survey_number),
            is_compound=is_compound_survey(body.survey_number),
            party_count=body.party_count,
            land_type=body.land_type,
            entity_type="parcel" if body.parcel_id else "manual-input",
            entity_id=body.parcel_id or "ad-hoc",
        )
    except ModelUnavailableError:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "ML model unavailable; no prediction was generated",
                "model": land_nature_model.status(),
                "disclaimer": DISCLAIMER,
            },
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Model inference timed out")
    return envelope


# ---------------------------------------------------------------------------
# Staging & Ingestion endpoints
# ---------------------------------------------------------------------------


@router.get("/staging/summary", response_model=dict)
async def staging_summary(
    current_user: User = Depends(require_role(STAFF_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    from app.models.import_staging import ImportedLandDetail, ImportedLandParty

    total_parcels = (await db.execute(select(func.count(ImportedLandDetail.id)))).scalar() or 0
    total_parties = (await db.execute(select(func.count(ImportedLandParty.id)))).scalar() or 0
    gov_parcels = (
        await db.execute(
            select(func.count(ImportedLandDetail.id)).where(
                ImportedLandDetail.land_nature_label == "government"
            )
        )
    ).scalar() or 0
    pvt_parcels = (
        await db.execute(
            select(func.count(ImportedLandDetail.id)).where(
                ImportedLandDetail.land_nature_label == "private"
            )
        )
    ).scalar() or 0
    total_area = (
        await db.execute(select(func.sum(ImportedLandDetail.area_hectares)))
    ).scalar() or 0

    villages_res = await db.execute(
        select(ImportedLandDetail.raw_village)
        .distinct()
        .where(ImportedLandDetail.raw_village.isnot(None))
    )
    villages = [v[0] for v in villages_res.all() if v[0]]

    files_res = await db.execute(select(ImportedLandDetail.source_file).distinct())
    source_files = [f[0] for f in files_res.all() if f[0]]

    return {
        "total_parcels": total_parcels,
        "total_parties": total_parties,
        "government_parcels": gov_parcels,
        "private_parcels": pvt_parcels,
        "total_area_hectares": float(total_area),
        "villages": villages,
        "source_files": source_files,
        "document_title": 'Details of Survey Numbers for "S.O. 1988E"',
        "document_publish_date": "22/06/2020",
    }


@router.get("/staging/parcels")
async def list_staging_parcels(
    page: int = 1,
    page_size: int = 20,
    village: Optional[str] = None,
    land_nature: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(require_role(STAFF_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    from app.models.import_staging import ImportedLandDetail

    query = select(ImportedLandDetail)
    if village:
        query = query.where(ImportedLandDetail.raw_village.ilike(f"%{village}%"))
    if land_nature:
        query = query.where(ImportedLandDetail.land_nature_label == land_nature)
    if search:
        query = query.where(
            (ImportedLandDetail.raw_survey_number.ilike(f"%{search}%"))
            | (ImportedLandDetail.raw_village.ilike(f"%{search}%"))
            | (ImportedLandDetail.source_sno.ilike(f"%{search}%"))
        )

    count_res = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_res.scalar() or 0

    offset = (page - 1) * page_size
    query = query.order_by(ImportedLandDetail.created_at.asc()).offset(offset).limit(page_size)
    items_res = await db.execute(query)
    rows = items_res.scalars().all()

    items = []
    for r in rows:
        items.append(
            {
                "id": str(r.id),
                "source_sno": r.source_sno,
                "raw_district": r.raw_district,
                "raw_sub_district": r.raw_sub_district,
                "raw_village": r.raw_village,
                "raw_survey_number": r.raw_survey_number,
                "raw_area": r.raw_area,
                "raw_land_type": r.raw_land_type,
                "raw_land_nature": r.raw_land_nature,
                "raw_land_category": r.raw_land_category,
                "village_norm": r.village_norm,
                "survey_number_norm": r.survey_number_norm,
                "area_hectares": float(r.area_hectares) if r.area_hectares else None,
                "land_type_mapped": r.land_type_mapped,
                "ownership_status_mapped": r.ownership_status_mapped,
                "land_nature_label": r.land_nature_label,
                "party_count": r.party_count,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
        )

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }


@router.get("/staging/parcels/{staging_id}/parties")
async def get_staging_parcel_parties(
    staging_id: uuid.UUID,
    current_user: User = Depends(require_role(STAFF_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    from app.models.import_staging import ImportedLandDetail, ImportedLandParty

    detail = (
        await db.execute(select(ImportedLandDetail).where(ImportedLandDetail.id == staging_id))
    ).scalar_one_or_none()
    if not detail:
        raise HTTPException(status_code=404, detail="Staging record not found")

    parties_res = await db.execute(
        select(ImportedLandParty).where(
            (ImportedLandParty.imported_detail_id == staging_id)
            | (
                (ImportedLandParty.source_sno == detail.source_sno)
                & (ImportedLandParty.source_file == detail.source_file)
            )
        )
    )
    parties = parties_res.scalars().all()

    return [
        {
            "id": str(p.id),
            "source_sno": p.source_sno,
            "raw_name": p.raw_name,
            "name_norm": p.name_norm,
            "raw_address": p.raw_address,
            "raw_type": p.raw_type,
            "party_type": p.party_type,
            "area_hectares": float(p.area_hectares) if p.area_hectares else None,
        }
        for p in parties
    ]


@router.post("/staging/promote")
async def promote_staging_to_project(
    body: dict,
    current_user: User = Depends(require_role(["super_admin", "agency", "state_authority"])),
    db: AsyncSession = Depends(get_db),
):
    from app.models.import_staging import ImportedLandDetail, ImportedLandParty
    from app.models.land import LandParcel, LandOwner, LandType, OwnershipStatus, VerificationStatus
    from app.models.project import Project
    from app.models.state import State, District, Village

    project_id_str = body.get("project_id")
    if not project_id_str:
        raise HTTPException(status_code=400, detail="project_id is required")

    project_id = uuid.UUID(project_id_str)
    project = (
        await db.execute(select(Project).where(Project.id == project_id))
    ).scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Target project not found")

    staging_ids = body.get("staging_parcel_ids")
    if staging_ids:
        uuids = [uuid.UUID(sid) for sid in staging_ids]
        query = select(ImportedLandDetail).where(ImportedLandDetail.id.in_(uuids))
    else:
        query = select(ImportedLandDetail)
        if body.get("source_file"):
            query = query.where(ImportedLandDetail.source_file == body["source_file"])

    staging_parcels = (await db.execute(query)).scalars().all()
    if not staging_parcels:
        raise HTTPException(status_code=400, detail="No staging parcels found to promote")

    promoted_parcels = 0
    promoted_owners = 0

    # Ensure a fallback village exists under project's district
    district_id = project.district_id
    state_id = project.state_id

    for sp in staging_parcels:
        # Resolve village
        v_name = sp.village_norm or (
            sp.raw_village.split()[0] if sp.raw_village else "Default Village"
        )
        v_res = await db.execute(
            select(Village).where(
                Village.district_id == district_id,
                Village.name.ilike(f"%{v_name}%"),
            )
        )
        village = v_res.scalars().first()
        if not village:
            village = Village(
                district_id=district_id,
                name=sp.raw_village or v_name.title(),
                code=f"VIL-{sp.source_sno}",
                tehsil=sp.raw_sub_district or "Tehsil",
            )
            db.add(village)
            await db.flush()

        # Map types
        lt = LandType.agricultural
        if sp.land_type_mapped and hasattr(LandType, sp.land_type_mapped):
            lt = LandType(sp.land_type_mapped)

        own_stat = OwnershipStatus.private
        if sp.ownership_status_mapped and hasattr(OwnershipStatus, sp.ownership_status_mapped):
            own_stat = OwnershipStatus(sp.ownership_status_mapped)

        parcel = LandParcel(
            project_id=project.id,
            survey_number=sp.survey_number_norm or sp.raw_survey_number or sp.source_sno,
            village_id=village.id,
            district_id=district_id,
            state_id=state_id,
            area_hectares=sp.area_hectares or 0.1,
            land_type=lt,
            ownership_status=own_stat,
            verification_status=VerificationStatus.pending,
        )
        db.add(parcel)
        await db.flush()
        promoted_parcels += 1

        # Fetch parties
        parties_res = await db.execute(
            select(ImportedLandParty).where(
                (ImportedLandParty.imported_detail_id == sp.id)
                | (
                    (ImportedLandParty.source_sno == sp.source_sno)
                    & (ImportedLandParty.source_file == sp.source_file)
                )
            )
        )
        parties = parties_res.scalars().all()
        share_per_party = round(100.0 / max(1, len(parties)), 2)

        for p in parties:
            clean_name = (
                p.raw_name.split("\n")[0].strip() if p.raw_name else (p.name_norm or "Land Owner")
            )
            owner = LandOwner(
                parcel_id=parcel.id,
                full_name=clean_name[:200],
                aadhaar_masked="XXXX-XXXX-" + str(1000 + (promoted_owners % 8999)),
                phone=f"98{promoted_owners:08d}"[:10],
                share_percentage=share_per_party,
                ifsc="SBIN0001234",
                bank_account_masked="XX...XXXX" + str(1000 + (promoted_owners % 8999)),
            )
            db.add(owner)
            promoted_owners += 1

    await db.commit()
    return {
        "promoted_parcels": promoted_parcels,
        "promoted_owners": promoted_owners,
        "project_id": str(project.id),
        "message": f"Successfully promoted {promoted_parcels} parcels and {promoted_owners} land owners into project '{project.name}'.",
    }


@router.post("/ingest")
async def trigger_ingest(
    body: Optional[dict] = None,
    current_user: User = Depends(require_role(["super_admin", "agency"])),
    db: AsyncSession = Depends(get_db),
):
    from app.ml.ingest import run_ingestion

    file_path = body.get("file_path") if body else None
    if not file_path:
        # Search common locations for the bhoomirashi workbook
        candidates = [
            Path("[bhoomirashi_gov_in_auth_revamp_sdet1_cshtml_project_id_54637]_features.xlsx"),
            Path("../[bhoomirashi_gov_in_auth_revamp_sdet1_cshtml_project_id_54637]_features.xlsx"),
            Path("backend/[bhoomirashi_gov_in_auth_revamp_sdet1_cshtml_project_id_54637]_features.xlsx"),
        ]
        for p in candidates:
            if p.exists():
                file_path = str(p)
                break

    if not file_path or not Path(file_path).exists():
        raise HTTPException(
            status_code=404, detail=f"Bhoomi Rashi workbook not found at {file_path}"
        )

    try:
        report = await run_ingestion(db, file_path)
        return {
            "source_file": report.source_file,
            "land_rows_seen": report.land_rows_seen,
            "land_rows_loaded": report.land_rows_loaded,
            "land_rows_rejected": report.land_rows_rejected,
            "land_rows_duplicate": report.land_rows_duplicate,
            "party_rows_seen": report.party_rows_seen,
            "party_rows_loaded": report.party_rows_loaded,
            "party_rows_rejected": report.party_rows_rejected,
            "party_rows_duplicate": report.party_rows_duplicate,
            "document_title": report.document_title,
            "document_publish_date": report.document_publish_date,
        }
    except Exception as e:
        logger.exception("Error ingesting Bhoomi Rashi workbook")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
