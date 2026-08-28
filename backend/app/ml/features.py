"""Shared feature construction for the land-nature screening model.

Used by BOTH the offline training script and inference-time preprocessing so
training/serving skew cannot occur. Features are intentionally simple,
explainable, and derived only from non-sensitive parcel attributes.
"""

import math
from typing import Optional

NUMERIC_FEATURES = ["log_area", "survey_head", "is_compound", "party_count"]
CATEGORICAL_FEATURES = ["village", "land_type"]
ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def build_features(
    village: Optional[str],
    area_hectares: Optional[float],
    survey_head: Optional[int],
    is_compound: bool,
    party_count: int,
    land_type: Optional[str],
) -> dict:
    """Build the model input feature vector from parcel attributes.

    Missing numerics are imputed with the training-set medians stored in the
    artifact; here we just emit None and let the sklearn pipeline handle them.
    """
    area = float(area_hectares) if area_hectares is not None and area_hectares > 0 else None
    return {
        "log_area": math.log(area) if area else None,
        "survey_head": float(survey_head) if survey_head is not None else None,
        "is_compound": 1.0 if is_compound else 0.0,
        "party_count": float(max(party_count or 0, 0)),
        "village": village or "__missing__",
        "land_type": land_type or "__missing__",
    }
