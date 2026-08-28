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

CATEGORY_MODEL_PATH = (
    BASE_DIR
    / "artifacts"
    / "category_model.txt"
)

CATEGORY_LABELS_PATH = (
    BASE_DIR
    / "artifacts"
    / "category_labels.json"
)

SUBCATEGORY_MODEL_PATH = (
    BASE_DIR
    / "artifacts"
    / "subcategory_model.txt"
)

SUBCATEGORY_LABELS_PATH = (
    BASE_DIR
    / "artifacts"
    / "subcategory_labels.json"
)


def load_json(path):
    with open(
        path,
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
    Reproduce the category-model validation split.
    """

    grouped = defaultdict(list)

    for ticket in tickets:
        grouped[ticket["category"]].append(ticket)

    rng = random.Random(seed)

    train_data = []
    validation_data = []

    for category, category_tickets in grouped.items():

        shuffled = category_tickets.copy()
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


def build_category_subcategory_map(
    tickets,
    subcategory_to_label,
):
    """
    Map each category to the valid subcategory labels
    belonging to that category.
    """

    mapping = defaultdict(set)

    for ticket in tickets:

        category = ticket["category"]
        subcategory = ticket.get("subcategory")

        if (
            category == "UNCLASSIFIED"
            or subcategory is None
        ):
            continue

        mapping[category].add(
            subcategory_to_label[
                subcategory
            ]
        )

    return {
        category: sorted(labels)
        for category, labels in mapping.items()
    }


def main():
    data = load_json(DATASET_PATH)

    all_tickets = data["tickets"]

    # Same split used by category training.
    train_data, validation_data = (
        stratified_split(
            all_tickets
        )
    )

    # Subcategory model excludes UNCLASSIFIED.
    validation_subcategory_data = [
        ticket
        for ticket in validation_data
        if (
            ticket["category"] != "UNCLASSIFIED"
            and ticket.get("subcategory") is not None
        )
    ]

    print(
        f"Total tickets: {len(all_tickets)}"
    )

    print(
        f"Category validation tickets: "
        f"{len(validation_data)}"
    )

    print(
        f"Subcategory validation tickets: "
        f"{len(validation_subcategory_data)}"
    )

    # -------------------------------------------------
    # LOAD LABELS
    # -------------------------------------------------

    category_labels = load_json(
        CATEGORY_LABELS_PATH
    )

    subcategory_labels = load_json(
        SUBCATEGORY_LABELS_PATH
    )

    category_to_label = (
        category_labels["category_to_label"]
    )

    label_to_category = {
        int(key): value
        for key, value
        in category_labels[
            "label_to_category"
        ].items()
    }

    subcategory_to_label = (
        subcategory_labels[
            "subcategory_to_label"
        ]
    )

    label_to_subcategory = {
        int(key): value
        for key, value
        in subcategory_labels[
            "label_to_subcategory"
        ].items()
    }

    category_to_subcategory_labels = (
        build_category_subcategory_map(
            all_tickets,
            subcategory_to_label,
        )
    )

    # -------------------------------------------------
    # LOAD MODELS
    # -------------------------------------------------

    category_model = lgb.Booster(
        model_file=str(
            CATEGORY_MODEL_PATH
        )
    )

    subcategory_model = lgb.Booster(
        model_file=str(
            SUBCATEGORY_MODEL_PATH
        )
    )

    # -------------------------------------------------
    # CATEGORY EVALUATION
    # -------------------------------------------------

    print(
        "\nGenerating category-validation embeddings..."
    )

    X_category = generate_embeddings(
        validation_data
    )

    category_probabilities = (
        category_model.predict(
            X_category
        )
    )

    category_predictions = (
        category_probabilities.argmax(
            axis=1
        )
    )

    category_correct = 0

    for ticket, predicted in zip(
        validation_data,
        category_predictions,
    ):
        actual = category_to_label[
            ticket["category"]
        ]

        if int(predicted) == int(actual):
            category_correct += 1

    category_accuracy = (
        category_correct
        / len(validation_data)
    )

    # -------------------------------------------------
    # SUBCATEGORY EVALUATION
    # -------------------------------------------------

    print(
        "\nGenerating subcategory-validation embeddings..."
    )

    X_subcategory = generate_embeddings(
        validation_subcategory_data
    )

    subcategory_probabilities = (
        subcategory_model.predict(
            X_subcategory
        )
    )

    global_subcategory_predictions = (
        subcategory_probabilities.argmax(
            axis=1
        )
    )

    global_subcategory_correct = 0
    constrained_oracle_correct = 0
    end_to_end_correct = 0

    category_correct_subcategory_correct = 0
    category_correct_subcategory_total = 0

    category_errors = []
    end_to_end_errors = []

    # -------------------------------------------------
    # ALIGN CATEGORY PREDICTIONS
    # -------------------------------------------------

    validation_indices = {
        id(ticket): index
        for index, ticket
        in enumerate(validation_data)
    }

    # -------------------------------------------------
    # EVALUATE EACH SUBCATEGORY TICKET
    # -------------------------------------------------

    for (
        ticket,
        probability,
        global_prediction,
    ) in zip(
        validation_subcategory_data,
        subcategory_probabilities,
        global_subcategory_predictions,
    ):

        actual_category = ticket[
            "category"
        ]

        actual_subcategory = ticket[
            "subcategory"
        ]

        actual_category_label = (
            category_to_label[
                actual_category
            ]
        )

        actual_subcategory_label = (
            subcategory_to_label[
                actual_subcategory
            ]
        )

        # -----------------------------------------
        # GLOBAL SUBCATEGORY
        # -----------------------------------------

        if (
            int(global_prediction)
            == int(actual_subcategory_label)
        ):
            global_subcategory_correct += 1

        # -----------------------------------------
        # ORACLE CATEGORY CONSTRAINT
        # -----------------------------------------

        allowed_labels = (
            category_to_subcategory_labels[
                actual_category
            ]
        )

        oracle_prediction = max(
            allowed_labels,
            key=lambda label: float(
                probability[label]
            ),
        )

        if (
            int(oracle_prediction)
            == int(actual_subcategory_label)
        ):
            constrained_oracle_correct += 1

        # -----------------------------------------
        # FIND CATEGORY MODEL PREDICTION
        # -----------------------------------------

        category_index = (
            validation_indices[
                id(ticket)
            ]
        )

        predicted_category_label = int(
            category_predictions[
                category_index
            ]
        )

        predicted_category = (
            label_to_category[
                predicted_category_label
            ]
        )

        # -----------------------------------------
        # END-TO-END MASK
        # -----------------------------------------

        if predicted_category in (
            category_to_subcategory_labels
        ):

            allowed_end_to_end = (
                category_to_subcategory_labels[
                    predicted_category
                ]
            )

            end_to_end_prediction = max(
                allowed_end_to_end,
                key=lambda label: float(
                    probability[label]
                ),
            )

            predicted_subcategory = (
                label_to_subcategory[
                    end_to_end_prediction
                ]
            )

            if (
                predicted_category
                == actual_category
            ):
                category_correct_subcategory_total += 1

                if (
                    predicted_subcategory
                    == actual_subcategory
                ):
                    category_correct_subcategory_correct += 1

            if (
                predicted_category
                == actual_category
                and
                predicted_subcategory
                == actual_subcategory
            ):
                end_to_end_correct += 1

            if (
                predicted_category
                != actual_category
                or
                predicted_subcategory
                != actual_subcategory
            ):
                end_to_end_errors.append(
                    {
                        "subject": ticket[
                            "subject"
                        ],
                        "actual_category":
                            actual_category,
                        "predicted_category":
                            predicted_category,
                        "actual_subcategory":
                            actual_subcategory,
                        "predicted_subcategory":
                            predicted_subcategory,
                        "category_confidence":
                            float(
                                category_probabilities[
                                    category_index
                                ][
                                    predicted_category_label
                                ]
                            ),
                        "subcategory_confidence":
                            float(
                                probability[
                                    end_to_end_prediction
                                ]
                            ),
                    }
                )

        # -----------------------------------------
        # CATEGORY ERROR LOG
        # -----------------------------------------

        if (
            predicted_category
            != actual_category
        ):
            category_errors.append(
                {
                    "subject": ticket[
                        "subject"
                    ],
                    "actual": actual_category,
                    "predicted": predicted_category,
                    "confidence": float(
                        category_probabilities[
                            category_index
                        ][predicted_category_label]
                    ),
                }
            )

    # -------------------------------------------------
    # RESULTS
    # -------------------------------------------------

    total_category = len(
        validation_data
    )

    total_subcategory = len(
        validation_subcategory_data
    )

    print("\n" + "=" * 100)
    print("END-TO-END CLASSIFICATION EVALUATION")
    print("=" * 100)

    print(
        f"Category validation accuracy: "
        f"{category_accuracy:.2%}"
    )

    print(
        f"Global subcategory accuracy: "
        f"{global_subcategory_correct / total_subcategory:.2%}"
    )

    print(
        f"Oracle constrained subcategory accuracy: "
        f"{constrained_oracle_correct / total_subcategory:.2%}"
    )

    print(
        f"End-to-end category → subcategory accuracy: "
        f"{end_to_end_correct / total_subcategory:.2%}"
    )

    print(
        f"\nCategory-correct subcategory accuracy: "
        f"{category_correct_subcategory_correct / category_correct_subcategory_total:.2%}"
        if category_correct_subcategory_total
        else "\nCategory-correct subcategory accuracy: N/A"
    )

    print(
        f"\nCategory errors: "
        f"{len(category_errors)}"
    )

    print(
        f"End-to-end errors: "
        f"{len(end_to_end_errors)}"
    )

    # -------------------------------------------------
    # CATEGORY ERRORS
    # -------------------------------------------------

    print(
        "\nCATEGORY ERRORS"
    )
    print("=" * 100)

    if not category_errors:
        print("NONE")
    else:
        for error in category_errors:
            print(
                f"{error['actual']:15}"
                f" -> "
                f"{error['predicted']:15}"
                f" | "
                f"{error['confidence']:.3f}"
                f" | "
                f"{error['subject']}"
            )

    # -------------------------------------------------
    # END-TO-END ERRORS
    # -------------------------------------------------

    print(
        "\nEND-TO-END ERRORS"
    )
    print("=" * 100)

    if not end_to_end_errors:
        print("NONE")
    else:
        for error in end_to_end_errors:
            print(
                f"{error['actual_category']:12}"
                f" / "
                f"{error['actual_subcategory']:25}"
                f" -> "
                f"{error['predicted_category']:12}"
                f" / "
                f"{error['predicted_subcategory']:25}"
                f" | "
                f"Cat: "
                f"{error['category_confidence']:.3f}"
                f" | "
                f"Sub: "
                f"{error['subcategory_confidence']:.3f}"
                f" | "
                f"{error['subject']}"
            )

    # -------------------------------------------------
    # ERROR PAIRS
    # -------------------------------------------------

    error_pairs = Counter(
        (
            error["actual_category"],
            error["predicted_category"],
            error["actual_subcategory"],
            error["predicted_subcategory"],
        )
        for error in end_to_end_errors
    )

    print(
        "\nEND-TO-END ERROR PAIRS"
    )
    print("=" * 100)

    if not error_pairs:
        print("NONE")
    else:
        for (
            pair,
            count,
        ) in error_pairs.most_common():

            (
                actual_category,
                predicted_category,
                actual_subcategory,
                predicted_subcategory,
            ) = pair

            print(
                f"{actual_category:12}"
                f"/"
                f"{actual_subcategory:25}"
                f" -> "
                f"{predicted_category:12}"
                f"/"
                f"{predicted_subcategory:25}"
                f": {count}"
            )


if __name__ == "__main__":
    main()