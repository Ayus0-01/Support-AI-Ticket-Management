import json
from pathlib import Path
from collections import defaultdict
import random

import lightgbm as lgb


DATASET_PATH = (
    Path(__file__).parent 
    / "datasets"
    / "severity_seed_data_v2.json"
)

def load_dataset():
    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def stratified_split(
    tickets,
    train_ratio=0.70,
    seed=42
):
    """
    Split severity data while preserving
    the severity distribution.
    """

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
    """
    Convert structured ticket information
    into numerical features for LightGBM.
    """

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
                f"Unknown category in severity dataset: "
                f"{category}"
            )

        features.append([
            scope_map.get(
                ticket.get("affected_scope"),
                0
            ),

            blocked_map.get(
                ticket.get("work_blocked"),
                0
            ),

            urgency_map.get(
                ticket.get("urgent_feeling"),
                0
            ),

            int(
                ticket.get(
                    "workaround_available",
                    False
                )
            ),

            category_map[category],
        ])

    return features


def create_labels(
    train_data,
    validation_data
):
    """
    Convert severity names into numeric labels.
    """

    severities = [
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    ]

    severity_to_label = {
        severity: index
        for index, severity
        in enumerate(severities)
    }

    label_to_severity = {
        index: severity
        for severity, index
        in severity_to_label.items()
    }

    y_train = [
        severity_to_label[
            ticket["severity"]
        ]
        for ticket in train_data
    ]

    y_validation = [
        severity_to_label[
            ticket["severity"]
        ]
        for ticket in validation_data
    ]

    return (
        y_train,
        y_validation,
        severity_to_label,
        label_to_severity,
    )


def train_severity_model(
    X_train,
    y_train
):
    """
    Train LightGBM severity classifier.
    """

    model = lgb.LGBMClassifier(
        objective="multiclass",
        num_class=4,
        n_estimators=100,
        learning_rate=0.05,
        num_leaves=15,
        max_depth=-1,
        random_state=42,
        verbosity=-1,
    )

    model.fit(
        X_train,
        y_train
    )

    return model


def evaluate_model(
    model,
    X_validation,
    y_validation,
    validation_data,
    label_to_severity
):
    """
    Evaluate severity predictions.
    """

    probabilities = model.predict_proba(
        X_validation
    )

    predictions = probabilities.argmax(
        axis=1
    )

    correct = 0

    print("\nSEVERITY VALIDATION RESULTS")
    print("=" * 80)

    for (
        ticket,
        actual,
        predicted,
        probability
    ) in zip(
        validation_data,
        y_validation,
        predictions,
        probabilities
    ):

        actual_severity = label_to_severity[
            int(actual)
        ]

        predicted_severity = label_to_severity[
            int(predicted)
        ]

        confidence = float(
            probability[predicted]
        )

        if actual == predicted:
            correct += 1

        print(
            f"{actual_severity:10} | "
            f"Predicted: {predicted_severity:10} | "
            f"Confidence: {confidence:.3f} | "
            f"Scope: {ticket['affected_scope']:13} | "
            f"Blocked: {ticket['work_blocked']}"
        )

    accuracy = (
        correct / len(y_validation)
        if y_validation
        else 0
    )

    print("\n" + "=" * 80)

    print(
        f"Correct predictions: "
        f"{correct}/{len(y_validation)}"
    )

    print(
        f"Validation accuracy: "
        f"{accuracy:.2%}"
    )


def save_model(
    model,
    severity_to_label,
    label_to_severity
):
    """
    Save severity model and label mappings.
    """

    artifacts_dir = (
        Path(__file__).parent / "artifacts"
    )

    artifacts_dir.mkdir(
        exist_ok=True
    )

    model_path = (
        artifacts_dir /
        "severity_model.txt"
    )

    labels_path = (
        artifacts_dir /
        "severity_labels.json"
    )

    model.booster_.save_model(
        str(model_path)
    )

    with open(
        labels_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            {
                "severity_to_label":
                    severity_to_label,

                "label_to_severity": {
                    str(key): value
                    for key, value
                    in label_to_severity.items()
                },
            },
            file,
            indent=4
        )

    print("\nSeverity model artifacts saved:")
    print(
        f"Model:  {model_path}"
    )

    print(
        f"Labels: {labels_path}"
    )


def main():

    data = load_dataset()

    tickets = data["tickets"]

    print(
        f"Loaded {len(tickets)} severity tickets."
    )

    train_data, validation_data = (
        stratified_split(tickets)
    )

    print(
        f"Training tickets: "
        f"{len(train_data)}"
    )

    print(
        f"Validation tickets: "
        f"{len(validation_data)}"
    )

    X_train = encode_features(
        train_data
    )

    X_validation = encode_features(
        validation_data
    )

    (
        y_train,
        y_validation,
        severity_to_label,
        label_to_severity,
    ) = create_labels(
        train_data,
        validation_data
    )

    print("\nSeverity labels:")
    print(severity_to_label)

    print(
        "\nTraining LightGBM severity model..."
    )

    model = train_severity_model(
        X_train,
        y_train
    )

    print(
        "Severity training complete."
    )

    evaluate_model(
        model,
        X_validation,
        y_validation,
        validation_data,
        label_to_severity
    )

    save_model(
        model,
        severity_to_label,
        label_to_severity
    )


if __name__ == "__main__":
    main()