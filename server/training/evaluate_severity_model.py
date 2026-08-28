import json
import random
from collections import defaultdict, Counter
from pathlib import Path

import lightgbm as lgb


BASE_DIR = Path(__file__).parent

DATASET_PATH = (
    BASE_DIR
    / "datasets"
    / "severity_seed_data_v2.json"
)

MODEL_PATH = (
    BASE_DIR
    / "artifacts"
    / "severity_model.txt"
)

SEVERITIES = [
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
]


def load_dataset():
    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def stratified_split(
    tickets,
    train_ratio=0.70,
    seed=42,
):
    grouped = defaultdict(list)

    for ticket in tickets:
        grouped[ticket["severity"]].append(ticket)

    rng = random.Random(seed)

    train_data = []
    validation_data = []

    for severity, severity_tickets in grouped.items():

        shuffled = severity_tickets.copy()
        rng.shuffle(shuffled)

        split_index = int(
            len(shuffled) * train_ratio
        )

        train_data.extend(
            shuffled[:split_index]
        )

        validation_data.extend(
            shuffled[split_index:]
        )

    rng.shuffle(train_data)
    rng.shuffle(validation_data)

    return train_data, validation_data


def encode_features(tickets):
    scope_map = {
        "JUST_ME": 0,
        "TEAM": 1,
        "DEPARTMENT": 2,
        "ORGANISATION": 3,
    }

    blocked_map = {
        "NO": 0,
        "PARTIALLY": 1,
        "YES": 2,
    }

    urgency_map = {
        "LOW": 0,
        "MEDIUM": 1,
        "HIGH": 2,
    }

    category_map = {
        "ACCESS": 0,
        "APPLICATION": 1,
        "EMAIL": 2,
        "HARDWARE": 3,
        "NETWORK": 4,
        "PRINTER": 5,
        "SECURITY": 6,
        "SOFTWARE": 7,
        "UNCLASSIFIED": 8,
        "VPN": 9,
    }

    features = []

    for ticket in tickets:

        category = ticket.get("category")

        if category not in category_map:
            raise ValueError(
                f"Unknown category: {category}"
            )

        features.append([
            scope_map.get(
                ticket.get("affected_scope"),
                0,
            ),
            blocked_map.get(
                ticket.get("work_blocked"),
                0,
            ),
            urgency_map.get(
                ticket.get("urgent_feeling"),
                0,
            ),
            int(
                ticket.get(
                    "workaround_available",
                    False,
                )
            ),
            category_map[category],
        ])

    return features


def encode_labels(tickets):
    severity_to_label = {
        severity: index
        for index, severity
        in enumerate(SEVERITIES)
    }

    return [
        severity_to_label[
            ticket["severity"]
        ]
        for ticket in tickets
    ]


def main():
    data = load_dataset()
    tickets = data["tickets"]

    train_data, validation_data = (
        stratified_split(tickets)
    )

    X_validation = encode_features(
        validation_data
    )

    y_validation = encode_labels(
        validation_data
    )

    model = lgb.Booster(
        model_file=str(MODEL_PATH)
    )

    probabilities = model.predict(
        X_validation
    )

    predictions = probabilities.argmax(
        axis=1
    )

    # -------------------------------------------------
    # OVERALL
    # -------------------------------------------------

    correct = sum(
        actual == predicted
        for actual, predicted
        in zip(
            y_validation,
            predictions,
        )
    )

    accuracy = (
        correct / len(y_validation)
        if y_validation
        else 0
    )

    print("=" * 90)
    print("SEVERITY MODEL EVALUATION")
    print("=" * 90)

    print(
        f"Total tickets: {len(tickets)}"
    )

    print(
        f"Training tickets: {len(train_data)}"
    )

    print(
        f"Validation tickets: "
        f"{len(validation_data)}"
    )

    print(
        f"\nOverall accuracy: "
        f"{accuracy:.2%}"
    )

    print(
        f"Correct predictions: "
        f"{correct}/{len(y_validation)}"
    )

    # -------------------------------------------------
    # CONFUSION MATRIX
    # -------------------------------------------------

    matrix = {
        actual: {
            predicted: 0
            for predicted in SEVERITIES
        }
        for actual in SEVERITIES
    }

    for actual, predicted in zip(
        y_validation,
        predictions,
    ):
        actual_name = SEVERITIES[
            int(actual)
        ]

        predicted_name = SEVERITIES[
            int(predicted)
        ]

        matrix[actual_name][
            predicted_name
        ] += 1

    print(
        "\nCONFUSION MATRIX"
    )
    print("=" * 90)

    print(
        f"{'Actual / Predicted':20}",
        end="",
    )

    for severity in SEVERITIES:
        print(
            f"{severity:12}",
            end="",
        )

    print()

    print("-" * 90)

    for actual in SEVERITIES:

        print(
            f"{actual:20}",
            end="",
        )

        for predicted in SEVERITIES:
            print(
                f"{matrix[actual][predicted]:12}",
                end="",
            )

        print()

    # -------------------------------------------------
    # PER-SEVERITY PERFORMANCE
    # -------------------------------------------------

    print(
        "\nPER-SEVERITY PERFORMANCE"
    )
    print("=" * 90)

    actual_counts = Counter()
    correct_counts = Counter()

    for actual, predicted in zip(
        y_validation,
        predictions,
    ):

        actual_name = SEVERITIES[
            int(actual)
        ]

        actual_counts[
            actual_name
        ] += 1

        if actual == predicted:
            correct_counts[
                actual_name
            ] += 1

    for severity in SEVERITIES:

        total = actual_counts[
            severity
        ]

        correct_for_class = (
            correct_counts[
                severity
            ]
        )

        class_accuracy = (
            correct_for_class / total
            if total
            else 0
        )

        print(
            f"{severity:10} | "
            f"{correct_for_class:2}/{total:2} | "
            f"{class_accuracy:.2%}"
        )

    # -------------------------------------------------
    # CONFIDENCE ANALYSIS
    # -------------------------------------------------

    print(
        "\nCONFIDENCE ANALYSIS"
    )
    print("=" * 90)

    correct_confidences = []
    incorrect_confidences = []

    for actual, predicted, probability in zip(
        y_validation,
        predictions,
        probabilities,
    ):

        confidence = float(
            probability[predicted]
        )

        if actual == predicted:
            correct_confidences.append(
                confidence
            )
        else:
            incorrect_confidences.append(
                confidence
            )

    if correct_confidences:
        print(
            f"Average correct confidence: "
            f"{sum(correct_confidences) / len(correct_confidences):.3f}"
        )

        print(
            f"Minimum correct confidence: "
            f"{min(correct_confidences):.3f}"
        )

        print(
            f"Maximum correct confidence: "
            f"{max(correct_confidences):.3f}"
        )

    if incorrect_confidences:
        print(
            f"Average incorrect confidence: "
            f"{sum(incorrect_confidences) / len(incorrect_confidences):.3f}"
        )

        print(
            f"Minimum incorrect confidence: "
            f"{min(incorrect_confidences):.3f}"
        )

        print(
            f"Maximum incorrect confidence: "
            f"{max(incorrect_confidences):.3f}"
        )

    # -------------------------------------------------
    # MISCLASSIFICATIONS
    # -------------------------------------------------

    print(
        "\nMISCLASSIFICATIONS"
    )
    print("=" * 90)

    found_errors = False

    for ticket, actual, predicted, probability in zip(
        validation_data,
        y_validation,
        predictions,
        probabilities,
    ):

        if actual == predicted:
            continue

        found_errors = True

        actual_name = SEVERITIES[
            int(actual)
        ]

        predicted_name = SEVERITIES[
            int(predicted)
        ]

        confidence = float(
            probability[predicted]
        )

        print(
            f"Actual: {actual_name:10} | "
            f"Predicted: {predicted_name:10} | "
            f"Confidence: {confidence:.3f} | "
            f"Category: {ticket['category']:12} | "
            f"Scope: {ticket['affected_scope']:13} | "
            f"Blocked: {ticket['work_blocked']}"
        )

    if not found_errors:
        print("NONE")


if __name__ == "__main__":
    main()