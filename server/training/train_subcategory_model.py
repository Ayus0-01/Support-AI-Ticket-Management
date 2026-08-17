import json
from pathlib import Path
from collections import defaultdict
import random

import lightgbm as lgb

from apps.tickets.classification.embeddings import generate_embedding


DATASET_PATH = Path(__file__).parent / "category_seed_data.json"


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
    Split tickets while preserving the
    subcategory distribution.
    """

    grouped = defaultdict(list)

    for ticket in tickets:

        key = (
            ticket["category"],
            ticket["subcategory"]
        )

        grouped[key].append(ticket)

    rng = random.Random(seed)

    train_data = []
    validation_data = []

    for key, subcategory_tickets in grouped.items():

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
    """
    Generate embeddings using the same
    embedding system as category classification.
    """

    embeddings = []

    for index, ticket in enumerate(
        tickets,
        start=1
    ):

        embedding = generate_embedding(
            ticket["subject"],
            ticket["description"]
        )

        embeddings.append(embedding)

        print(
            f"Generated embedding "
            f"{index}/{len(tickets)}",
            end="\r"
        )

    print()

    return embeddings


def create_labels(
    train_data,
    validation_data
):
    """
    Create numeric labels for subcategories.
    """

    subcategories = sorted(
        {
            ticket["subcategory"]
            for ticket in (
                train_data +
                validation_data
            )
        }
    )

    subcategory_to_label = {
        subcategory: index
        for index, subcategory
        in enumerate(subcategories)
    }

    label_to_subcategory = {
        index: subcategory
        for subcategory, index
        in subcategory_to_label.items()
    }

    y_train = [
        subcategory_to_label[
            ticket["subcategory"]
        ]
        for ticket in train_data
    ]

    y_validation = [
        subcategory_to_label[
            ticket["subcategory"]
        ]
        for ticket in validation_data
    ]

    return (
        y_train,
        y_validation,
        subcategory_to_label,
        label_to_subcategory,
    )


def train_model(
    X_train,
    y_train,
    num_classes
):
    """
    Train the LightGBM subcategory classifier.
    """

    model = lgb.LGBMClassifier(
        objective="multiclass",
        num_class=num_classes,
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
    label_to_subcategory
):
    """
    Evaluate subcategory predictions.
    """

    probabilities = model.predict_proba(
        X_validation
    )

    predictions = probabilities.argmax(
        axis=1
    )

    correct = 0

    print(
        "\nSUBCATEGORY VALIDATION RESULTS"
    )

    print("=" * 100)

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

        actual_subcategory = (
            label_to_subcategory[
                int(actual)
            ]
        )

        predicted_subcategory = (
            label_to_subcategory[
                int(predicted)
            ]
        )

        confidence = float(
            probability[predicted]
        )

        if actual == predicted:
            correct += 1

        print(
            f"{ticket['category']:12} | "
            f"Actual: "
            f"{actual_subcategory:25} | "
            f"Predicted: "
            f"{predicted_subcategory:25} | "
            f"Confidence: "
            f"{confidence:.3f}"
        )

    accuracy = (
        correct / len(y_validation)
        if y_validation
        else 0
    )

    print(
        "\n" + "=" * 100
    )

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
    subcategory_to_label,
    label_to_subcategory
):
    """
    Save the trained model and label mappings.
    """

    artifacts_dir = (
        Path(__file__).parent /
        "artifacts"
    )

    artifacts_dir.mkdir(
        exist_ok=True
    )

    model_path = (
        artifacts_dir /
        "subcategory_model.txt"
    )

    labels_path = (
        artifacts_dir /
        "subcategory_labels.json"
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
                "subcategory_to_label":
                    subcategory_to_label,

                "label_to_subcategory": {
                    str(key): value
                    for key, value
                    in label_to_subcategory.items()
                },
            },
            file,
            indent=4
        )

    print(
        "\nSubcategory model artifacts saved:"
    )

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
        f"Loaded {len(tickets)} "
        f"subcategory tickets."
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

    print(
        "\nGenerating training embeddings..."
    )

    X_train = generate_embeddings(
        train_data
    )

    print(
        "Generating validation embeddings..."
    )

    X_validation = generate_embeddings(
        validation_data
    )

    (
        y_train,
        y_validation,
        subcategory_to_label,
        label_to_subcategory,
    ) = create_labels(
        train_data,
        validation_data
    )

    print(
        "\nSubcategory labels:"
    )

    print(
        subcategory_to_label
    )

    num_classes = len(
        subcategory_to_label
    )

    print(
        f"\nNumber of subcategories: "
        f"{num_classes}"
    )

    print(
        "\nTraining LightGBM "
        "subcategory model..."
    )

    model = train_model(
        X_train,
        y_train,
        num_classes
    )

    print(
        "Subcategory training complete."
    )

    evaluate_model(
        model,
        X_validation,
        y_validation,
        validation_data,
        label_to_subcategory
    )

    save_model(
        model,
        subcategory_to_label,
        label_to_subcategory
    )


if __name__ == "__main__":
    main()