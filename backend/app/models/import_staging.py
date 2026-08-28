"""Staging tables for BhoomiRashi workbook imports.

Raw workbook values are preserved verbatim in `raw_*` columns for auditability;
normalized/derived columns power search, matching, and model inference. Rows
live outside the transactional parcel/owner tables until reviewed, so
unvalidated source data never contaminates production entities.
"""

import uuid
from sqlalchemy import Column, String, Numeric, Text, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base, TimestampMixin


class ImportedLandDetail(Base, TimestampMixin):
    __tablename__ = "imported_land_details"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_file = Column(String(500), nullable=False, index=True)
    source_sno = Column(String(50), nullable=False, index=True)
    dedupe_key = Column(String(400), nullable=False, unique=True, index=True)

    # Raw workbook values, preserved exactly
    raw_district = Column(Text, nullable=True)
    raw_sub_district = Column(Text, nullable=True)
    raw_village = Column(Text, nullable=True)
    raw_survey_number = Column(Text, nullable=True)
    raw_area = Column(Text, nullable=True)
    raw_description = Column(Text, nullable=True)
    raw_land_type = Column(Text, nullable=True)
    raw_land_nature = Column(Text, nullable=True)
    raw_land_category = Column(Text, nullable=True)
    raw_additional_details = Column(Text, nullable=True)

    # Normalized / canonical fields (derived, never overwrite raw)
    district_norm = Column(String(200), nullable=True, index=True)
    sub_district_norm = Column(String(200), nullable=True, index=True)
    village_norm = Column(String(200), nullable=True, index=True)
    survey_number_norm = Column(String(200), nullable=True, index=True)
    survey_number_head = Column(Integer, nullable=True)
    is_compound_survey = Column(Boolean, nullable=False, default=False)
    area_hectares = Column(Numeric(12, 6), nullable=True)
    land_type_mapped = Column(String(50), nullable=True)
    land_type_mapped_ok = Column(Boolean, nullable=False, default=False)
    ownership_status_mapped = Column(String(50), nullable=True)
    ownership_status_mapped_ok = Column(Boolean, nullable=False, default=False)
    land_category = Column(String(100), nullable=True)

    # Source-reported land nature — the ML label. NOT verified legal title.
    land_nature_label = Column(String(50), nullable=True, index=True)
    party_count = Column(Integer, nullable=False, default=0)


class ImportedLandParty(Base, TimestampMixin):
    __tablename__ = "imported_land_parties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_file = Column(String(500), nullable=False, index=True)
    source_sno = Column(String(50), nullable=False, index=True)
    dedupe_key = Column(String(600), nullable=False, unique=True, index=True)

    # Raw preserved
    raw_name = Column(Text, nullable=True)
    raw_address = Column(Text, nullable=True)
    raw_type = Column(Text, nullable=True)
    raw_area = Column(Text, nullable=True)

    # Normalized for search/matching only
    name_norm = Column(String(400), nullable=True, index=True)
    address_norm = Column(Text, nullable=True)
    party_type = Column(String(100), nullable=True)
    party_type_mapped_ok = Column(Boolean, nullable=False, default=False)
    area_hectares = Column(Numeric(12, 6), nullable=True)
    imported_detail_id = Column(
        UUID(as_uuid=True),
        ForeignKey("imported_land_details.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
