"""Server-side inference service for the land-nature screening model.

Loads the joblib artifact lazily (never at import time), reports truthful
availability status, and NEVER fabricates predictions. If the artifact is
missing or incompatible, endpoints receive ``status="unavailable"`` and the
API returns a 503 envelope rather than a fake result.
"""

import logging
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import joblib

from app.core.config import settings
from app.ml.features import build_features

logger = logging.getLogger(__name__)

DISCLAIMER = (
    "AI-assisted decision support only; not a legal ownership determination. "
    "Verify through the official land-records workflow."
)


class ModelUnavailableError(RuntimeError):
    """Raised when the ML artifact is missing, incompatible, or disabled."""


class LandNatureModel:
    """Thread-safe lazy loader around the trained screening model."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._artifact: Optional[dict] = None
        self._load_error: Optional[str] = None

    def _load(self) -> dict:
        if self._artifact is not None:
            return self._artifact
        with self._lock:
            if self._artifact is not None:
                return self._artifact
            if not settings.ML_ENABLED:
                self._load_error = "ML integration disabled by configuration (ML_ENABLED=false)"
                raise ModelUnavailableError(self._load_error)
            path = Path(settings.ML_MODEL_PATH)
            if not path.exists():
                self._load_error = f"Model artifact not found at configured ML_MODEL_PATH"
                logger.warning("ML model unavailable: %s", self._load_error)
                raise ModelUnavailableError(self._load_error)
            try:
                artifact = joblib.load(path)
                # Minimal compatibility check: expected keys and fitted pipeline
                for key in ("model", "model_name", "model_version", "label_classes"):
                    if key not in artifact:
                        raise ValueError(f"artifact missing key '{key}'")
                if not hasattr(artifact["model"], "predict_proba"):
                    raise ValueError("artifact model has no predict_proba")
                if artifact["model_version"] != settings.ML_MODEL_VERSION:
                    raise ValueError(
                        f"artifact version {artifact['model_version']} != configured "
                        f"{settings.ML_MODEL_VERSION}"
                    )
            except ModelUnavailableError:
                raise
            except Exception as exc:  # incompatible artifact
                self._load_error = f"Incompatible model artifact: {exc}"
                logger.warning("ML model unavailable: %s", self._load_error)
                raise ModelUnavailableError(self._load_error)
            self._load_error = None
            self._artifact = artifact
            logger.info(
                "ML model %s v%s loaded from %s",
                artifact["model_name"], artifact["model_version"], path,
            )
            return self._artifact

    def status(self) -> dict:
        """Truthful availability status without internal paths."""
        try:
            artifact = self._load()
            return {
                "name": artifact["model_name"],
                "version": artifact["model_version"],
                "status": "available",
                "trained_at": artifact.get("trained_at"),
            }
        except ModelUnavailableError:
            return {
                "name": "land-nature-screening",
                "version": settings.ML_MODEL_VERSION,
                "status": "unavailable",
                "trained_at": None,
            }

    def predict(
        self,
        *,
        village: Optional[str],
        area_hectares: Optional[float],
        survey_head: Optional[int],
        is_compound: bool,
        party_count: int,
        land_type: Optional[str],
        entity_type: str,
        entity_id: str,
    ) -> dict:
        """Run screening inference and build the versioned response envelope."""
        artifact = self._load()
        model = artifact["model"]
        features = build_features(
            village=village,
            area_hectares=area_hectares,
            survey_head=survey_head,
            is_compound=is_compound,
            party_count=party_count,
            land_type=land_type,
        )
        import pandas as pd

        from app.ml.features import ALL_FEATURES

        frame = pd.DataFrame([[features[name] for name in ALL_FEATURES]], columns=ALL_FEATURES)
        probabilities = model.predict_proba(frame)[0]
        classes = list(artifact["label_classes"])
        best = max(range(len(classes)), key=lambda i: probabilities[i])
        label = classes[best]
        score = float(probabilities[best])
        government_p = float(probabilities[classes.index("government")]) if "government" in classes else None

        # Feature-level explanation from logistic coefficients is possible but
        # only meaningful in aggregate; report truthful factor summary instead.
        explanation = {
            "summary": (
                f"Screening model estimates this parcel's source-reported nature is "
                f"'{label}' (probability {score:.2f}). Trained on {artifact['metrics']['n_rows']}"
                f" Khordha notification records; cross-validated balanced accuracy "
                f"{artifact['metrics']['cv_balanced_accuracy_mean']}."
            ),
            "factors": [
                {"name": "village", "value": village},
                {"name": "area_hectares", "value": area_hectares},
                {"name": "party_count", "value": party_count},
                {"name": "is_compound_survey", "value": is_compound},
            ],
        }
        return {
            "model": {
                "name": artifact["model_name"],
                "version": artifact["model_version"],
                "status": "available",
            },
            "prediction": {
                "label": label,
                "score": round(score, 4),
                "government_probability": round(government_p, 4) if government_p is not None else None,
                "confidence": None,  # model provides calibrated-ish probabilities only
                "unit": "probability",
            },
            "explanation": explanation,
            "input_snapshot": {"entity_type": entity_type, "entity_id": entity_id},
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "disclaimer": DISCLAIMER,
        }


land_nature_model = LandNatureModel()
