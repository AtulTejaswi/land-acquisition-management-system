"""GIS service — GeoJSON generation and parcel import logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional
import json
import uuid

from app.models.land import LandParcel
from app.schemas.parcel import ParcelResponse, LandOwnerResponse, PaginatedParcels
from app.models.audit import AuditLog


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


async def build_geojson_featurecollection(
    db: AsyncSession,
    project_id: Optional[uuid.UUID] = None,
    district_id: Optional[uuid.UUID] = None,
    state_id: Optional[uuid.UUID] = None,
) -> dict:
    query = (
        select(LandParcel)
        .where(LandParcel.is_deleted == False)
        .options(
            selectinload(LandParcel.village),
            selectinload(LandParcel.district),
            selectinload(LandParcel.state),
        )
    )
    if project_id:
        query = query.where(LandParcel.project_id == project_id)
    if district_id:
        query = query.where(LandParcel.district_id == district_id)
    if state_id:
        query = query.where(LandParcel.state_id == state_id)

    result = await db.execute(query)
    parcels = result.scalars().unique().all()

    features = []
    for parcel in parcels:
        geom = None
        if parcel.geom:
            try:
                geom = json.loads(parcel.geom) if isinstance(parcel.geom, str) else parcel.geom
            except (json.JSONDecodeError, TypeError):
                geom = None
        if geom:
            features.append(
                {
                    "type": "Feature",
                    "id": str(parcel.id),
                    "geometry": geom,
                    "properties": {
                        "id": str(parcel.id),
                        "survey_number": parcel.survey_number,
                        "area_hectares": float(parcel.area_hectares)
                        if parcel.area_hectares
                        else None,
                        "land_type": parcel.land_type.value
                        if hasattr(parcel.land_type, "value")
                        else str(parcel.land_type),
                        "ownership_status": parcel.ownership_status.value
                        if hasattr(parcel.ownership_status, "value")
                        else str(parcel.ownership_status),
                        "verification_status": parcel.verification_status.value
                        if hasattr(parcel.verification_status, "value")
                        else str(parcel.verification_status),
                        "village_name": parcel.village.name if parcel.village else None,
                        "district_name": parcel.district.name if parcel.district else None,
                        "state_name": parcel.state.name if parcel.state else None,
                        "project_id": str(parcel.project_id),
                    },
                }
            )

    return {"type": "FeatureCollection", "features": features}


async def import_geojson_features(
    db: AsyncSession,
    features: list,
    project_id: Optional[uuid.UUID] = None,
    imported_by: Optional[uuid.UUID] = None,
) -> int:
    imported = 0
    for feature in features:
        geometry = feature.get("geometry")
        props = feature.get("properties", {})
        if not geometry:
            continue

        parcel = LandParcel(
            project_id=project_id or uuid.UUID(props.get("project_id", str(uuid.uuid4()))),
            survey_number=props.get("survey_number", f"IMPORT-{imported + 1}"),
            village_id=uuid.UUID(props["village_id"]) if props.get("village_id") else uuid.uuid4(),
            district_id=uuid.UUID(props["district_id"])
            if props.get("district_id")
            else uuid.uuid4(),
            state_id=uuid.UUID(props["state_id"]) if props.get("state_id") else uuid.uuid4(),
            area_hectares=props.get("area_hectares"),
            geom=json.dumps(geometry),
            land_type=props.get("land_type", "other"),
            ownership_status=props.get("ownership_status", "private"),
        )
        db.add(parcel)
        imported += 1

    if imported > 0 and imported_by:
        audit = AuditLog(
            entity_type="gis_import",
            entity_id=uuid.uuid4(),
            action="import",
            performed_by=imported_by,
            new_value={"count": imported},
            remarks=f"Imported {imported} parcels from GeoJSON",
        )
        db.add(audit)

    await db.commit()
    return imported
