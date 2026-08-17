import json
from pathlib import Path

import lightgbm as lgb

from .embeddings import generate_embedding


# server/
BASE_DIR = Path(__file__).resolve().parents[3]

ARTIFACTS_DIR = BASE_DIR / "training" / "artifacts"

MODEL_PATH = ARTIFACTS_DIR / "category_model.txt"
LABELS_PATH = ARTIFACTS_DIR / "category_labels.json"

# Evidence-based baseline from our validation experiment.
FAST_PATH_THRESHOLD = 0.75
UNCLASSIFIED_THRESHOLD = 0.40

SECURITY_KEYWORDS = {
    "phishing",
    "malware",
    "ransomware",
    "data breach",
    "security breach",
    "account compromised",
    "credential theft",
    "stolen credentials",
    "suspicious login",
    "unauthorized access",
}

# Load the trained LightGBM model once.
_model = lgb.Booster(
    model_file=str(MODEL_PATH)
)


# Load category label mappings.
with open(
    LABELS_PATH,
    "r",
    encoding="utf-8",
) as file:
    _label_data = json.load(file)


LABEL_TO_CATEGORY = {
    int(label): category
    for label, category
    in _label_data["label_to_category"].items()
}
CATEGORY_TRAINING_COUNTS = _label_data.get(
    "category_training_counts",
    {}
)

def contains_security_keyword(subject, description):
    """
    Check whether the ticket contains a security-related keyword.
    """

    text = f"{subject or ''} {description or ''}".lower()

    return any(
        keyword in text
        for keyword in SECURITY_KEYWORDS
    )

def predict_category(
    subject,
    description,
    channel="",
):
    """
    Predict the category of a support ticket.

    Returns:
        category
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

    predicted_label = int(
        probabilities.argmax()
    )

    confidence = float(
        probabilities[predicted_label]
    )

    category = LABEL_TO_CATEGORY[
        predicted_label
    ]

    if confidence < UNCLASSIFIED_THRESHOLD:
        return {
            "category": "UNCLASSIFIED",
            "confidence": round(confidence, 3),
            "route": "LLM",
        }

    if confidence < FAST_PATH_THRESHOLD:
        route = "LLM"

    else:
        route = "FAST"

        category_count = CATEGORY_TRAINING_COUNTS.get(
            category,
            0
        )

        if category_count < 30:
            route = "LLM"

    if (
        channel.lower() == "email"
        and len(description or "") > 1500
    ):
        route = "LLM"

    if contains_security_keyword(
        subject,
        description,
    ):
        route = "LLM"

    return {
        "category": category,
        "confidence": round(confidence, 3),
        "route": route,
    }

def predict_category_fast(
    subject,
    description,
):
    """
    FAST-only category prediction for live preview.

    This function never routes to the LLM.
    """

    embedding = generate_embedding(
        subject,
        description,
    )

    probabilities = _model.predict(
        [embedding]
    )[0]

    predicted_label = int(
        probabilities.argmax()
    )

    confidence = float(
        probabilities[predicted_label]
    )

    category = LABEL_TO_CATEGORY[
        predicted_label
    ]

    if confidence < UNCLASSIFIED_THRESHOLD:
        category = "UNCLASSIFIED"

    return {
        "category": category,
        "confidence": round(
            confidence,
            3
        ),
        "route": "FAST",
    }