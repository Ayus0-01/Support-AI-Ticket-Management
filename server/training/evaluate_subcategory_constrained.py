import json
import random
from collections import defaultdict, Counter
from pathlib import Path

import lightgbm as lgb

from apps.tickets.classification.embeddings import generate_embedding


BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = (
    BASE_DIR
    / "datasets"
    / "category_seed_data_v2_final.json"
)

MODEL_PATH = (
    BASE_DIR
    / "artifacts"
    / "subcategory_model.txt"
)

LABELS_PATH = (
    BASE_DIR
    / "artifacts"
    / "subcategory_labels.json"
)


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
    """
    Reproduce the same subcategory-stratified
    split used during training.
    """

    grouped = defaultdict(list)

    for ticket in tickets:

        if (
            ticket["category"] == "UNCLASSIFIED"
            or ticket.get("subcategory") is None
        ):
            continue

        key = (
            ticket["category"],
            ticket["subcategory"],
        )

        grouped[key].append(ticket)

    rng = random.Random(seed)

    train_data = []
    validation_data = []

    for (
        key,
        subcategory_tickets,
    ) in grouped.items():

        shuffled = subcategory_tickets.copy()

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


def generate_embeddings(tickets):
    embeddings = []

    for index, ticket in enumerate(
        tickets,
        start=1,
    ):

        embedding = generate_embedding(
            ticket["subject"],
            ticket["description"],
        )

        embeddings.append(embedding)

        print(
            f"Generated embedding "
            f"{index}/{len(tickets)}",
            end="\r",
        )

    print()

    return embeddings


def load_labels():
    with open(
        LABELS_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def build_category_label_map(
    tickets,
    subcategory_to_label,
):
    """
    Map each category to the numeric labels
    corresponding to its valid subcategories.
    """

    category_to_labels = defaultdict(set)

    for ticket in tickets:

        category = ticket["category"]
        subcategory = ticket["subcategory"]

        if (
            category == "UNCLASSIFIED"
            or subcategory is None
        ):
            continue

        label = subcategory_to_label[
            subcategory
        ]

        category_to_labels[
            category
        ].add(label)

    return {
        category: sorted(labels)
        for category, labels
        in category_to_labels.items()
    }


def evaluate(
    model,
    probabilities,
    validation_data,
    subcategory_to_label,
    label_to_subcategory,
    category_to_labels,
):
    global_correct = 0
    oracle_correct = 0

    global_predictions = []
    oracle_predictions = []

    oracle_confidences = []

    for (
        ticket,
        probability,
    ) in zip(
        validation_data,
        probabilities,
    ):

        actual_subcategory = (
            ticket["subcategory"]
        )

        actual_label = (
            subcategory_to_label[
                actual_subcategory
            ]
        )

        # -----------------------------------------
        # GLOBAL PREDICTION
        # -----------------------------------------

        global_label = int(
            probability.argmax()
        )

        if global_label == actual_label:
            global_correct += 1

        global_predictions.append(
            global_label
        )

        # -----------------------------------------
        # CATEGORY-CONSTRAINED PREDICTION
        # -----------------------------------------

        allowed_labels = category_to_labels[
            ticket["category"]
        ]

        constrained_label = max(
            allowed_labels,
            key=lambda label: float(
                probability[label]
            ),
        )

        constrained_confidence = float(
            probability[constrained_label]
        )

        if constrained_label == actual_label:
            oracle_correct += 1

        oracle_predictions.append(
            constrained_label
        )

        oracle_confidences.append(
            constrained_confidence
        )

    total = len(validation_data)

    global_accuracy = (
        global_correct / total
        if total
        else 0.0
    )

    oracle_accuracy = (
        oracle_correct / total
        if total
        else 0.0
    )

    print("\n" + "=" * 100)
    print("SUBCATEGORY CONSTRAINED EVALUATION")
    print("=" * 100)

    print(
        f"Validation tickets: {total}"
    )

    print(
        f"\nGlobal accuracy: "
        f"{global_accuracy:.2%}"
    )

    print(
        f"Category-constrained accuracy: "
        f"{oracle_accuracy:.2%}"
    )

    print(
        f"\nGlobal correct: "
        f"{global_correct}/{total}"
    )

    print(
        f"Constrained correct: "
        f"{oracle_correct}/{total}"
    )

    if oracle_confidences:
        print(
            f"\nAverage constrained confidence: "
            f"{sum(oracle_confidences) / len(oracle_confidences):.3f}"
        )

    # -----------------------------------------
    # REMAINING CONSTRAINED ERRORS
    # -----------------------------------------

    print(
        "\nREMAINING CATEGORY-CONSTRAINED ERRORS"
    )
    print("=" * 100)

    constrained_errors = []

    for (
        ticket,
        predicted_label,
        probability,
    ) in zip(
        validation_data,
        oracle_predictions,
        probabilities,
    ):

        actual_label = (
            subcategory_to_label[
                ticket["subcategory"]
            ]
        )

        if predicted_label == actual_label:
            continue

        predicted_subcategory = (
            label_to_subcategory[
                str(predicted_label)
            ]
        )

        confidence = float(
            probability[predicted_label]
        )

        constrained_errors.append(
            (
                ticket["category"],
                ticket["subcategory"],
                predicted_subcategory,
                confidence,
                ticket["subject"],
            )
        )

    if not constrained_errors:
        print("NONE")
    else:
        for (
            category,
            actual,
            predicted,
            confidence,
            subject,
        ) in constrained_errors:

            print(
                f"{category:12} | "
                f"Actual: {actual:25} | "
                f"Predicted: {predicted:25} | "
                f"Confidence: {confidence:.3f} | "
                f"{subject}"
            )

    # -----------------------------------------
    # CONSTRAINED ERROR COUNTS
    # -----------------------------------------

    error_counts = Counter(
        (
            actual,
            predicted,
        )
        for (
            category,
            actual,
            predicted,
            confidence,
            subject,
        ) in constrained_errors
    )

    print(
        "\nCONSTRAINED ERROR PAIRS"
    )
    print("=" * 100)

    if error_counts:

        for (
            (actual, predicted),
            count,
        ) in error_counts.most_common():

            print(
                f"{actual:25}"
                f" -> "
                f"{predicted:25}"
                f" : {count}"
            )

    else:
        print("NONE")


def main():

    data = load_dataset()

    all_tickets = data["tickets"]

    train_data, validation_data = (
        stratified_split(
            all_tickets
        )
    )

    print(
        f"Validation tickets: "
        f"{len(validation_data)}"
    )

    labels = load_labels()

    subcategory_to_label = (
        labels["subcategory_to_label"]
    )

    label_to_subcategory = (
        labels["label_to_subcategory"]
    )

    category_to_labels = (
        build_category_label_map(
            train_data + validation_data,
            subcategory_to_label,
        )
    )

    print(
        "\nCategory candidate sets:"
    )

    for category in sorted(
        category_to_labels
    ):

        subcategories = [
            label_to_subcategory[
                str(label)
            ]
            for label in category_to_labels[
                category
            ]
        ]

        print(
            f"{category:15} -> "
            f"{', '.join(subcategories)}"
        )

    print(
        "\nGenerating validation embeddings..."
    )

    X_validation = generate_embeddings(
        validation_data
    )

    model = lgb.Booster(
        model_file=str(MODEL_PATH)
    )

    probabilities = model.predict(
        X_validation
    )

    evaluate(
        model,
        probabilities,
        validation_data,
        subcategory_to_label,
        label_to_subcategory,
        category_to_labels,
    )


if __name__ == "__main__":
    main()