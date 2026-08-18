import json
from pathlib import Path
from collections import defaultdict
import random
import lightgbm as lgb

from apps.tickets.classification.embeddings import generate_embedding


DATASET_PATH = Path(__file__).parent / "category_seed_data.json"


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data


def stratified_split(tickets, train_ratio=0.70, seed=42):
    """
    Split tickets into training and validation sets while
    preserving the category distribution.
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

        split_index = int(len(shuffled) * train_ratio)

        train_data.extend(shuffled[:split_index])
        validation_data.extend(shuffled[split_index:])

    rng.shuffle(train_data)
    rng.shuffle(validation_data)

    return train_data, validation_data


def generate_ticket_embeddings(tickets):
    """
    Generate one embedding vector for every ticket.
    """

    embeddings = []

    for index, ticket in enumerate(tickets, start=1):

        embedding = generate_embedding(
            ticket["subject"],
            ticket["description"]
        )

        embeddings.append(embedding)

        print(
            f"Generated embedding {index}/{len(tickets)}",
            end="\r"
        )

    print()

    return embeddings

def create_category_labels(train_data, validation_data):
    """
    Convert category names into numeric labels for LightGBM.
    """

    categories = sorted(
        {
            ticket["category"]
            for ticket in train_data + validation_data
        }
    )

    category_to_label = {
        category: index
        for index, category in enumerate(categories)
    }

    label_to_category = {
        index: category
        for category, index in category_to_label.items()
    }

    category_training_counts = {
        category: sum(
            1
            for ticket in train_data
            if ticket["category"] == category
        )
        for category in categories
    }

    y_train = [
        category_to_label[ticket["category"]]
        for ticket in train_data
    ]

    y_validation = [
        category_to_label[ticket["category"]]
        for ticket in validation_data
    ]

    return (
        y_train,
        y_validation,
        category_to_label,
        label_to_category,
        category_training_counts,
    )

def train_category_model(X_train, y_train):
    """
    Train LightGBM category classifier.
    """

    model = lgb.LGBMClassifier(
        objective="multiclass",
        num_class=7,
        n_estimators=100,
        learning_rate=0.05,
        num_leaves=15,
        max_depth=-1,
        random_state=42,
        verbosity=-1,
    )

    model.fit(
        X_train,
        y_train,
    )

    return model

def save_category_model(
    model,
    category_to_label,
    label_to_category,
    category_training_counts,
):
    """
    Save the trained LightGBM model and category mappings.
    """

    artifacts_dir = Path(__file__).parent / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)

    model_path = artifacts_dir / "category_model.txt"
    labels_path = artifacts_dir / "category_labels.json"

    # Save LightGBM model
    model.booster_.save_model(str(model_path))

    # Save category mappings
    with open(labels_path, "w", encoding="utf-8") as file:
        json.dump(
            {
                "category_to_label": category_to_label,
                "label_to_category": {
                    str(key): value
                    for key, value in label_to_category.items()
                },
                "category_training_counts": category_training_counts,
            },
            file,
            indent=4,
        )

    print("\nModel artifacts saved:")
    print(f"Model:  {model_path}")
    print(f"Labels: {labels_path}")

def evaluate_category_model(
    model,
    X_validation,
    y_validation,
    validation_data,
    label_to_category,
):
    """
    Evaluate the trained LightGBM category classifier.
    """

    probabilities = model.predict_proba(X_validation)

    predictions = probabilities.argmax(axis=1)

    correct = 0

    print("\nVALIDATION RESULTS")
    print("=" * 70)

    for ticket, actual_label, predicted_label, probability in zip(
        validation_data,
        y_validation,
        predictions,
        probabilities,
    ):
        predicted_category = label_to_category[int(predicted_label)]
        actual_category = label_to_category[int(actual_label)]

        confidence = float(probability[predicted_label])

        if predicted_label == actual_label:
            correct += 1

        print(
            f"{ticket['subject'][:40]:40} | "
            f"Actual: {actual_category:12} | "
            f"Predicted: {predicted_category:12} | "
            f"Confidence: {confidence:.3f}"
        )

    accuracy = correct / len(y_validation)

    print("\n" + "=" * 70)
    print(f"Correct predictions: {correct}/{len(y_validation)}")
    print(f"Validation accuracy: {accuracy:.2%}")

def print_confusion_matrix(
    model,
    X_validation,
    y_validation,
    label_to_category,
):
    """
    Print a simple confusion matrix without adding
    another machine-learning dependency.
    """

    probabilities = model.predict_proba(X_validation)
    predictions = probabilities.argmax(axis=1)

    labels = sorted(label_to_category.keys())

    matrix = {
        actual: {
            predicted: 0
            for predicted in labels
        }
        for actual in labels
    }

    for actual, predicted in zip(y_validation, predictions):
        matrix[int(actual)][int(predicted)] += 1

    categories = [
        label_to_category[label]
        for label in labels
    ]

    print("\nCONFUSION MATRIX")
    print("=" * 100)

    print(
        f"{'Actual / Predicted':20}",
        end=""
    )

    for category in categories:
        print(f"{category:14}", end="")

    print()

    print("-" * 100)

    for actual_label in labels:

        actual_category = label_to_category[actual_label]

        print(
            f"{actual_category:20}",
            end=""
        )

        for predicted_label in labels:
            print(
                f"{matrix[actual_label][predicted_label]:14}",
                end=""
            )

        print()

def analyze_confidence(
    model,
    X_validation,
    y_validation,
):
    """
    Analyze prediction confidence for correct
    and incorrect validation predictions.
    """

    probabilities = model.predict_proba(X_validation)

    predictions = probabilities.argmax(axis=1)

    correct_confidences = []
    incorrect_confidences = []

    for actual, predicted, probability in zip(
        y_validation,
        predictions,
        probabilities,
    ):
        confidence = float(probability[predicted])

        if predicted == actual:
            correct_confidences.append(confidence)
        else:
            incorrect_confidences.append(confidence)

    print("\nCONFIDENCE ANALYSIS")
    print("=" * 70)

    print(
        f"Correct predictions:   {len(correct_confidences)}"
    )

    print(
        f"Incorrect predictions: {len(incorrect_confidences)}"
    )

    if correct_confidences:
        print(
            f"Minimum correct confidence: "
            f"{min(correct_confidences):.3f}"
        )

        print(
            f"Maximum correct confidence: "
            f"{max(correct_confidences):.3f}"
        )

        print(
            f"Average correct confidence: "
            f"{sum(correct_confidences) / len(correct_confidences):.3f}"
        )

    if incorrect_confidences:
        print(
            f"Minimum incorrect confidence: "
            f"{min(incorrect_confidences):.3f}"
        )

        print(
            f"Maximum incorrect confidence: "
            f"{max(incorrect_confidences):.3f}"
        )

        print(
            f"Average incorrect confidence: "
            f"{sum(incorrect_confidences) / len(incorrect_confidences):.3f}"
        )

def analyze_routing_thresholds(
    model,
    X_validation,
    y_validation,
):
    """
    Evaluate different confidence thresholds for the
    planned FAST-path / LLM-fallback architecture.
    """

    probabilities = model.predict_proba(X_validation)

    predictions = probabilities.argmax(axis=1)

    thresholds = [
        0.50,
        0.60,
        0.70,
        0.80,
        0.85,
        0.90,
    ]

    print("\nROUTING THRESHOLD ANALYSIS")
    print("=" * 100)

    for threshold in thresholds:

        fast_total = 0
        fast_correct = 0
        fallback_total = 0
        caught_errors = 0

        for actual, predicted, probability in zip(
            y_validation,
            predictions,
            probabilities,
        ):

            confidence = float(probability[predicted])

            if confidence >= threshold:

                fast_total += 1

                if predicted == actual:
                    fast_correct += 1

            else:

                fallback_total += 1

                if predicted != actual:
                    caught_errors += 1

        fast_errors = fast_total - fast_correct

        if fast_total:
            fast_accuracy = (
                fast_correct / fast_total
            ) * 100
        else:
            fast_accuracy = 0.0

        print(
            f"\nThreshold: {threshold:.2f}"
        )

        print(
            f"FAST path:           {fast_total}"
        )

        print(
            f"LLM fallback:        {fallback_total}"
        )

        print(
            f"FAST errors:         {fast_errors}"
        )

        print(
            f"Errors caught:       {caught_errors}"
        )

        print(
            f"FAST accuracy:       {fast_accuracy:.2f}%"
        )

def main():
    data = load_dataset()
    tickets = data["tickets"]

    print(f"Loaded {len(tickets)} tickets.")

    train_data, validation_data = stratified_split(tickets)

    print(f"Training tickets: {len(train_data)}")
    print(f"Validation tickets: {len(validation_data)}")

    print("\nGenerating training embeddings...")

    X_train = generate_ticket_embeddings(train_data)

    print("Generating validation embeddings...")

    X_validation = generate_ticket_embeddings(validation_data)

    (
        y_train,
        y_validation,
        category_to_label,
        label_to_category,
        category_training_counts,
    ) = create_category_labels(
        train_data,
        validation_data,
    )

    print("\nCategory labels:")
    print(category_to_label)

    print(f"\nTraining labels: {len(y_train)}")
    print(f"Validation labels: {len(y_validation)}")

    print("\nExample training label:")
    print(
        train_data[0]["category"],
        "→",
        y_train[0]
    )

    print("\nEmbedding generation complete.")

    print(f"Training vectors: {len(X_train)}")
    print(f"Validation vectors: {len(X_validation)}")

    if X_train:
        print(f"Embedding dimension: {len(X_train[0])}")

    if X_train and X_validation:
        print(
            "Validation dimension:",
            len(X_validation[0])
        )
        print("\nTraining LightGBM category model...")

    model = train_category_model(
        X_train,
        y_train,
    )

    print("LightGBM training complete.")

    evaluate_category_model(
        model,
        X_validation,
        y_validation,
        validation_data,
        label_to_category,
    )
    print_confusion_matrix(
        model,
        X_validation,
        y_validation,
        label_to_category,
    )
    analyze_confidence(
        model,
        X_validation,
        y_validation,
    )
    analyze_routing_thresholds(
        model,
        X_validation,
        y_validation,
    )
    save_category_model(
    model,
    category_to_label,
    label_to_category,
    category_training_counts,
    )

if __name__ == "__main__":
    main()