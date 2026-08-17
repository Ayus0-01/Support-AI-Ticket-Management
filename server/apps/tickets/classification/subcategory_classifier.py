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

    predicted_label = int(
        probabilities.argmax()
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

    predicted_label = int(
        probabilities.argmax()
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