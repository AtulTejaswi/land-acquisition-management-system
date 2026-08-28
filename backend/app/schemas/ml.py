"""Pydantic schemas for ML inference endpoints."""

from typing import Optional, List, Any
from pydantic import BaseModel, Field


class MlModelStatus(BaseModel):
    name: str
    version: str
    status: str = Field(..., description="available | unavailable | degraded")
    trained_at: Optional[str] = None


class MlPrediction(BaseModel):
    label: str
    score: float
    government_probability: Optional[float] = None
    confidence: Optional[float] = None
    unit: Optional[str] = None


class MlExplanationFactor(BaseModel):
    name: str
    value: Any


class MlExplanation(BaseModel):
    summary: str
    factors: List[MlExplanationFactor]


class MlInputSnapshot(BaseModel):
    entity_type: str = Field(..., description="project | parcel | party")
    entity_id: str


class MlPredictionResponse(BaseModel):
    model: MlModelStatus
    prediction: MlPrediction
    explanation: MlExplanation
    input_snapshot: MlInputSnapshot
    generated_at: str
    disclaimer: str


class MlHealthResponse(BaseModel):
    status: str
    model: MlModelStatus


class LandNaturePredictRequest(BaseModel):
    village: Optional[str] = Field(None, max_length=200)
    area_hectares: Optional[float] = Field(None, gt=0, le=100000)
    survey_number: Optional[str] = Field(None, max_length=200)
    party_count: int = Field(0, ge=0, le=10000)
    land_type: Optional[str] = Field(None, max_length=50)
    parcel_id: Optional[str] = None
