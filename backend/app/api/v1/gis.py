from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional
import json
import uuid

from app.db.session import get_db
from app.models.land import LandParcel
from app.models.state import Village, District, State
from app.models.user import User
from app.core.deps import require_role, get_current_user
from app.schemas.parcel import GeoJSONFeatureCollection

router = APIRouter(prefix="/gis", tags=["gis"])


@router.get("/parcels/geojson", response_model=dict)
async def get_parcels_geojson(
    project_id: Optional[uuid.UUID] = None,
    district_id: Optional[uuid.UUID] = None,
    state_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(LandParcel).where(LandParcel.is_deleted == False).options(
        selectinload(LandParcel.village),
        selectinload(LandParcel.district),
        selectinload(LandParcel.state),
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
            feature = {
                "type": "Feature",
                "id": str(parcel.id),
                "geometry": geom,
                "properties": {
                    "id": str(parcel.id),
                    "survey_number": parcel.survey_number,
                    "area_hectares": float(parcel.area_hectares) if parcel.area_hectares else None,
                    "land_type": parcel.land_type.value if hasattr(parcel.land_type, 'value') else str(parcel.land_type),
                    "ownership_status": parcel.ownership_status.value if hasattr(parcel.ownership_status, 'value') else str(parcel.ownership_status),
                    "verification_status": parcel.verification_status.value if hasattr(parcel.verification_status, 'value') else str(parcel.verification_status),
                    "village_name": parcel.village.name if parcel.village else None,
                    "district_name": parcel.district.name if parcel.district else None,
                    "state_name": parcel.state.name if parcel.state else None,
                    "project_id": str(parcel.project_id),
                }
            }
            features.append(feature)

    return {"type": "FeatureCollection", "features": features}


@router.get("/parcels/{parcel_id}/geojson")
async def get_single_parcel_geojson(
    parcel_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LandParcel).where(LandParcel.id == parcel_id).options(
            selectinload(LandParcel.village),
            selectinload(LandParcel.district),
            selectinload(LandParcel.state),
        )
    )
    parcel = result.scalar_one_or_none()
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")

    geom = None
    if parcel.geom:
        try:
            geom = json.loads(parcel.geom) if isinstance(parcel.geom, str) else parcel.geom
        except (json.JSONDecodeError, TypeError):
            geom = None

    return {
        "type": "Feature",
        "id": str(parcel.id),
        "geometry": geom,
        "properties": {
            "id": str(parcel.id),
            "survey_number": parcel.survey_number,
            "area_hectares": float(parcel.area_hectares) if parcel.area_hectares else None,
            "land_type": parcel.land_type.value if hasattr(parcel.land_type, 'value') else str(parcel.land_type),
            "verification_status": parcel.verification_status.value if hasattr(parcel.verification_status, 'value') else str(parcel.verification_status),
            "village_name": parcel.village.name if parcel.village else None,
            "district_name": parcel.district.name if parcel.district else None,
        }
    }


@router.post("/import-geojson")
async def import_geojson(
    file: UploadFile = File(...),
    project_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(require_role(["super_admin", "state_authority", "district_officer"])),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    try:
        geojson = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid GeoJSON file")

    if geojson.get("type") != "FeatureCollection":
        raise HTTPException(status_code=400, detail="File must be a GeoJSON FeatureCollection")

    features = geojson.get("features", [])
    imported = 0
    for feature in features:
        geometry = feature.get("geometry")
        props = feature.get("properties", {})
        if not geometry:
            continue

        parcel = LandParcel(
            project_id=project_id or uuid.UUID(props.get("project_id", str(uuid.uuid4()))),
            survey_number=props.get("survey_number", f"IMPORT-{imported+1}"),
            village_id=uuid.UUID(props["village_id"]) if props.get("village_id") else uuid.uuid4(),
            district_id=uuid.UUID(props["district_id"]) if props.get("district_id") else uuid.uuid4(),
            state_id=uuid.UUID(props["state_id"]) if props.get("state_id") else uuid.uuid4(),
            area_hectares=props.get("area_hectares"),
            geom=json.dumps(geometry),
            land_type=props.get("land_type", "other"),
            ownership_status=props.get("ownership_status", "private"),
        )
        db.add(parcel)
        imported += 1

    await db.commit()
    return {"message": f"Imported {imported} parcels", "count": imported}
