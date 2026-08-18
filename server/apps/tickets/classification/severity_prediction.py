import json
from pathlib import Path

import lightgbm as lgb


BASE_DIR = Path(__file__).resolve().parents[3]

ARTIFACTS_DIR = BASE_DIR / "training" / "artifacts"

MODEL_PATH = ARTIFACTS_DIR / "severity_model.txt"
LABELS_PATH = ARTIFACTS_DIR / "severity_labels.json"


# Load trained severity model once.
_model = lgb.Booster(
    model_file=str(MODEL_PATH)
)


# Load severity label mappings.
with open(
    LABELS_PATH,
    "r",
    encoding="utf-8"
) as file:
    _label_data = json.load(file)


LABEL_TO_SEVERITY = {
    int(label): severity
    for label, severity
    in _label_data["label_to_severity"].items()
}


SCOPE_MAP = {
    "JUST_ME": 0,
    "TEAM": 1,
    "DEPARTMENT": 2,
    "ORGANISATION": 3,
}


BLOCKED_MAP = {
    "NO": 0,
    "PARTIALLY": 1,
    "YES": 2,
}


URGENCY_MAP = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2,
}


CATEGORY_MAP = {
    "ACCESS": 0,
    "APPLICATION": 1,
    "EMAIL": 2,
    "HARDWARE": 3,
    "NETWORK": 4,
    "SOFTWARE": 5,
    "VPN": 6,
}


def encode_severity_features(
    affected_scope,
    work_blocked,
    urgent_feeling,
    workaround_available,
    category,
):
    """
    Convert structured ticket information
    into the same numerical features used
    during severity model training.
    """

    return [[
        SCOPE_MAP.get(
            affected_scope,
            0
        ),

        BLOCKED_MAP.get(
            work_blocked,
            0
        ),

        URGENCY_MAP.get(
            urgent_feeling,
            0
        ),

        int(
            workaround_available
            if workaround_available is not None
            else False
        ),

        CATEGORY_MAP.get(
            category,
            0
        ),
    ]]


def predict_severity(
    affected_scope,
    work_blocked,
    urgent_feeling,
    workaround_available,
    category,
):
    """
    Predict ticket severity using the trained
    LightGBM severity model.

    Returns:
        severity
        confidence
    """

    features = encode_severity_features(
        affected_scope=affected_scope,
        work_blocked=work_blocked,
        urgent_feeling=urgent_feeling,
        workaround_available=workaround_available,
        category=category,
    )

    probabilities = _model.predict(
        features
    )

    probabilities = probabilities[0]

    predicted_label = int(
        probabilities.argmax()
    )

    confidence = float(
        probabilities[predicted_label]
    )

    severity = LABEL_TO_SEVERITY[
        predicted_label
    ]

    return {
        "severity": severity,
        "confidence": round(
            confidence,
            3
        ),
    }