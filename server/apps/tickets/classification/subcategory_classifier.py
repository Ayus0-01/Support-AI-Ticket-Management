import json
from pathlib import Path

import lightgbm as lgb

from .embeddings import generate_embedding

BASE_DIR = Path(__file__).resolve().parents[3]

ARTIFACTS_DIR = BASE_DIR / "training" / "artifacts"

MODEL_PATH = ARTIFACTS_DIR / "subcategory_model.txt"
LABELS_PATH = ARTIFACTS_DIR / "subcategory_labels.json"

FAST_PATH_THRESHOLD = 0.70
UNCLASSIFIED_THRESHOLD = 0.40

CATEGORY_SUBCATEGORIES = {
    "ACCESS": {"Account lockout", "MFA", "Onboarding", "Password reset", "Permissions"},
    "APPLICATION": {"CRM", "ERP", "Integration failure", "Internal tool", "Performance"},
    "EMAIL": {"Calendar", "Distribution list", "Mailbox", "Spam", "Storage quota"},
    "HARDWARE": {"Desktop", "Docking station", "Laptop", "Mobile device", "Peripheral"},
    "NETWORK": {"Bandwidth", "Connectivity", "DNS", "LAN", "WiFi"},
    "PRINTER": {"Driver", "Not printing", "Quality", "Queue stuck", "Scan"},
    "SECURITY": {"Data request", "Malware", "Phishing report", "Suspicious activity"},
    "SOFTWARE": {"Compatibility", "Crash", "Installation", "Licensing", "Update"},
    "VPN": {"Certificate", "Client install", "Connection failure", "Timeout"},
}

_model = lgb.Booster(
    model_file=str(MODEL_PATH)
)

with open(
    LABELS_PATH,
    "r",
    encoding="utf-8",
) as file:
    _label_data = json.load(file)


LABEL_TO_SUBCATEGORY = {
    int(label): subcategory
    for label, subcategory
    in _label_data["label_to_subcategory"].items()
}


def predict_subcategory(
    subject,
    description,
    category,
):
    """
    Predict the subcategory of a support ticket.

    Returns:
        subcategory
        confidence
        route
    """

    embedding = generate_embedding(
        subject,
        description,
    )

    probabilities = _model.predict(
        [embedding]
    )

    probabilities = probabilities[0]

    allowed_subcategories = CATEGORY_SUBCATEGORIES.get(
        category,
        set(),
    )

    allowed_labels = [
        label
        for label, subcategory
        in LABEL_TO_SUBCATEGORY.items()
        if subcategory in allowed_subcategories
    ]

    if not allowed_labels:
        return {
            "subcategory": "UNCLASSIFIED",
            "confidence": 0.0,
            "route": "LLM",
        }

    predicted_label = max(
        allowed_labels,
        key=lambda label: float(probabilities[label]),
    )

    confidence = float(
        probabilities[predicted_label]
    )

    subcategory = LABEL_TO_SUBCATEGORY[
        predicted_label
    ]

    if confidence < UNCLASSIFIED_THRESHOLD:
        return {
            "subcategory": "UNCLASSIFIED",
            "confidence": round(
                confidence,
                3
            ),
            "route": "LLM",
        }

    route = (
        "FAST"
        if confidence >= FAST_PATH_THRESHOLD
        else "LLM"
    )

    return {
        "subcategory": subcategory,
        "confidence": round(
            confidence,
            3
        ),
        "route": route,
    }

def predict_subcategory_fast(
    subject,
    description,
    category,
):
    """
    FAST-only subcategory prediction for live preview.

    This function never routes to the LLM.
    """

    embedding = generate_embedding(
        subject,
        description,
    )

    probabilities = _model.predict(
        [embedding]
    )[0]

    allowed_subcategories = CATEGORY_SUBCATEGORIES.get(
        category,
        set(),
    )

    allowed_labels = [
        label
        for label, subcategory
        in LABEL_TO_SUBCATEGORY.items()
        if subcategory in allowed_subcategories
    ]

    if not allowed_labels:
        return {
            "subcategory": "UNCLASSIFIED",
            "confidence": 0.0,
            "route": "FAST",
        }

    predicted_label = max(
        allowed_labels,
        key=lambda label: float(probabilities[label]),
    )

    confidence = float(
        probabilities[predicted_label]
    )

    subcategory = LABEL_TO_SUBCATEGORY[
        predicted_label
    ]

    if confidence < UNCLASSIFIED_THRESHOLD:
        subcategory = "UNCLASSIFIED"

    return {
        "subcategory": subcategory,
        "confidence": round(
            confidence,
            3
        ),
        "route": "FAST",
    }