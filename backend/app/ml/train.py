"""Offline training for the land-nature screening model.

Administrative/explicit operation only — NEVER run at application startup and
never on production user-submitted data. Trains on the BhoomiRashi workbook
(after the same normalization used by ingestion) and writes a versioned joblib
artifact plus a metrics report.

Target: source-reported Land Nature (Government vs Private). This is a
screening aid over source-record characteristics, NOT a legal ownership
determination.

Usage:
    python -m app.ml.train --workbook /path/to/features.xlsx --out-dir app/ml/artifacts
"""

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import joblib

logger = logging.getLogger(__name__)

MODEL_NAME = "land-nature-screening"
MODEL_VERSION = "1.0.0"


def build_training_frame(workbook_path: str):
    """Parse the workbook and assemble (X, y) using shared normalization."""
    import pandas as pd

    from app.ml.features import ALL_FEATURES, build_features
    from app.ml.ingest import parse_workbook
    from app.ml.normalize import (
        is_compound_survey,
        map_land_type,
        normalize_text,
        survey_number_head,
    )

    parcels, parties, report = parse_workbook(workbook_path)
    party_counts: dict[str, int] = {}
    for party in parties:
        party_counts[party.source_sno] = party_counts.get(party.source_sno, 0) + 1

    rows, labels = [], []
    for parcel in parcels:
        if parcel.land_nature_label not in ("government", "private"):
            continue  # only supervised rows with a clean binary label
        land_type, _ = map_land_type(parcel.raw.get("land_type"))
        feats = build_features(
            village=parcel.village_norm,
            area_hectares=float(parcel.area_hectares) if parcel.area_hectares else None,
            survey_head=survey_number_head(parcel.raw.get("survey_number")),
            is_compound=is_compound_survey(parcel.raw.get("survey_number")),
            party_count=party_counts.get(parcel.source_sno, 0),
            land_type=normalize_text(land_type),
        )
        rows.append([feats[name] for name in ALL_FEATURES])
        labels.append(parcel.land_nature_label)

    return pd.DataFrame(rows, columns=ALL_FEATURES), labels, report


def train(workbook_path: str, out_dir: str) -> dict:
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import classification_report, f1_score, make_scorer, balanced_accuracy_score
    from sklearn.model_selection import StratifiedKFold, cross_val_score
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    from app.ml.features import CATEGORICAL_FEATURES, NUMERIC_FEATURES

    X, y, report = build_training_frame(workbook_path)
    n_gov = sum(1 for label in y if label == "government")
    n_total = len(y)
    logger.info("Training rows: %d (government: %d, private: %d)", n_total, n_gov, n_total - n_gov)
    if n_gov < 5 or (n_total - n_gov) < 5:
        raise SystemExit(
            f"Not enough supervised rows for both classes (government={n_gov}, "
            f"private={n_total - n_gov}). Refusing to train a meaningless model."
        )

    numeric = Pipeline(
        [("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
    )
    categorical = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocess = ColumnTransformer(
        [
            ("num", numeric, NUMERIC_FEATURES),
            ("cat", categorical, CATEGORICAL_FEATURES),
        ]
    )
    model = Pipeline(
        [
            ("preprocess", preprocess),
            (
                "clf",
                LogisticRegression(
                    class_weight="balanced", max_iter=1000, random_state=42
                ),
            ),
        ]
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_balanced = cross_val_score(model, X, y, cv=cv, scoring="balanced_accuracy")
    cv_f1_gov = cross_val_score(
        model, X, y, cv=cv, scoring="f1_macro"
    )

    model.fit(X, y)

    from sklearn.metrics import precision_recall_fscore_support

    # Honest in-sample report for the record; CV numbers above are the ones to quote.
    y_pred = model.predict(X)
    in_sample = classification_report(y, y_pred, output_dict=True, zero_division=0)

    metrics = {
        "n_rows": n_total,
        "n_government": n_gov,
        "n_private": n_total - n_gov,
        "cv_balanced_accuracy_mean": round(float(cv_balanced.mean()), 4),
        "cv_balanced_accuracy_std": round(float(cv_balanced.std()), 4),
        "cv_f1_macro_mean": round(float(cv_f1_gov.mean()), 4),
        "in_sample_classification_report": in_sample,
        "note": (
            "Cross-validated metrics are the honest estimate. The dataset is a single "
            "Khordha notification with 6 villages; expect weak generalization outside "
            "this district. Class distribution is heavily imbalanced (~9% government)."
        ),
    }

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    artifact = {
        "model": model,
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "label_classes": list(model.named_steps["clf"].classes_),
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "training_source": Path(workbook_path).name,
        "metrics": metrics,
    }
    artifact_path = out / "land_nature_model.joblib"
    joblib.dump(artifact, artifact_path)
    metrics_path = out / "land_nature_model_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2))
    logger.info("Artifact written to %s", artifact_path)
    logger.info("Metrics written to %s", metrics_path)
    print(json.dumps(metrics, indent=2)[:2000])
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the land-nature screening model offline")
    parser.add_argument("--workbook", required=True, help="Path to the BhoomiRashi XLSX workbook")
    parser.add_argument("--out-dir", default="app/ml/artifacts")
    args = parser.parse_args()
    train(args.workbook, args.out_dir)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
