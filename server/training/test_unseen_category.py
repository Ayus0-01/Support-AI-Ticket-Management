import json
from pathlib import Path
from collections import Counter


from apps.tickets.classification.category_classifier import predict_category


BASE_DIR = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    BASE_DIR
    / "training"
    / "unseen_category_test_data.json"
)


def load_test_data():
    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)["tickets"]


def print_confusion_matrix(results):
    categories = [
        "ACCESS",
        "APPLICATION",
        "EMAIL",
        "HARDWARE",
        "NETWORK",
        "SOFTWARE",
        "VPN",
    ]

    matrix = {
        actual: {
            predicted: 0
            for predicted in categories
        }
        for actual in categories
    }

    for result in results:
        actual = result["actual"]
        predicted = result["predicted"]

        if (
            actual in matrix
            and predicted in matrix[actual]
        ):
            matrix[actual][predicted] += 1

    print("\nCONFUSION MATRIX")
    print("=" * 105)

    header = (
        f"{'Actual / Predicted':<22}"
        + "".join(
            f"{category:<12}"
            for category in categories
        )
    )

    print(header)
    print("-" * 105)

    for actual in categories:
        row = f"{actual:<22}"

        for predicted in categories:
            row += f"{matrix[actual][predicted]:<12}"

        print(row)


def main():

    tickets = load_test_data()

    print("=" * 90)
    print("UNSEEN CATEGORY CLASSIFIER TEST")
    print("=" * 90)

    print(f"Loaded {len(tickets)} unseen tickets.")
    print("Threshold: 0.75")
    print()

    results = []

    for index, ticket in enumerate(
        tickets,
        start=1,
    ):

        prediction = predict_category(
            ticket["subject"],
            ticket["description"],
        )

        actual = ticket["category"]
        predicted = prediction["category"]
        confidence = prediction["confidence"]
        route = prediction["route"]

        correct = (
            predicted == actual
        )

        results.append(
            {
                "subject": ticket["subject"],
                "actual": actual,
                "predicted": predicted,
                "confidence": confidence,
                "route": route,
                "correct": correct,
            }
        )

        print(
            f"{index:02d}. "
            f"{ticket['subject']:<42} | "
            f"Actual: {actual:<12} | "
            f"Predicted: {predicted:<12} | "
            f"Confidence: {confidence:.3f} | "
            f"Route: {route}"
        )

    total = len(results)

    correct = sum(
        result["correct"]
        for result in results
    )

    incorrect = total - correct

    accuracy = (
        correct / total
        if total
        else 0
    )

    fast_results = [
        result
        for result in results
        if result["route"] == "FAST"
    ]

    llm_results = [
        result
        for result in results
        if result["route"] == "LLM"
    ]

    fast_correct = sum(
        result["correct"]
        for result in fast_results
    )

    llm_correct = sum(
        result["correct"]
        for result in llm_results
    )

    fast_accuracy = (
        fast_correct / len(fast_results)
        if fast_results
        else 0
    )

    llm_accuracy = (
        llm_correct / len(llm_results)
        if llm_results
        else 0
    )

    print("\n")
    print("=" * 90)
    print("UNSEEN TEST RESULTS")
    print("=" * 90)

    print(f"Total tickets:       {total}")
    print(f"Correct predictions: {correct}")
    print(f"Incorrect predictions: {incorrect}")

    print(
        f"Overall accuracy:    "
        f"{accuracy * 100:.2f}%"
    )

    print()
    print(f"FAST path:           {len(fast_results)}")
    print(f"LLM fallback:        {len(llm_results)}")

    if fast_results:
        print(
            f"FAST accuracy:       "
            f"{fast_accuracy * 100:.2f}%"
        )
    else:
        print("FAST accuracy:       N/A")

    if llm_results:
        print(
            f"LLM fallback accuracy: "
            f"{llm_accuracy * 100:.2f}%"
        )
    else:
        print("LLM fallback accuracy: N/A")

    wrong_predictions = [
        result
        for result in results
        if not result["correct"]
    ]

    print("\n")
    print("=" * 90)
    print("WRONG PREDICTIONS")
    print("=" * 90)

    if not wrong_predictions:
        print("None 🎯")

    else:
        for result in wrong_predictions:
            print(
                f"\nSubject:     {result['subject']}"
            )
            print(
                f"Actual:      {result['actual']}"
            )
            print(
                f"Predicted:   {result['predicted']}"
            )
            print(
                f"Confidence:  {result['confidence']:.3f}"
            )
            print(
                f"Route:       {result['route']}"
            )

    print("\n")
    print("=" * 90)
    print("LLM FALLBACK TICKETS")
    print("=" * 90)

    if not llm_results:
        print("None")

    else:
        for result in llm_results:
            print(
                f"{result['subject']:<42} | "
                f"Actual: {result['actual']:<12} | "
                f"Model: {result['predicted']:<12} | "
                f"Confidence: {result['confidence']:.3f}"
            )

    print("\n")
    print("=" * 90)
    print("LOWEST CONFIDENCE PREDICTIONS")
    print("=" * 90)

    lowest_confidence = sorted(
        results,
        key=lambda result: result["confidence"],
    )[:10]

    for result in lowest_confidence:
        status = (
            "CORRECT"
            if result["correct"]
            else "WRONG"
        )

        print(
            f"{result['subject']:<42} | "
            f"{result['confidence']:.3f} | "
            f"{result['route']:<4} | "
            f"{status}"
        )

    print("\n")
    print("=" * 90)
    print("CATEGORY-WISE RESULTS")
    print("=" * 90)

    categories = sorted(
        set(
            result["actual"]
            for result in results
        )
    )

    for category in categories:

        category_results = [
            result
            for result in results
            if result["actual"] == category
        ]

        category_correct = sum(
            result["correct"]
            for result in category_results
        )

        category_accuracy = (
            category_correct
            / len(category_results)
        )

        print(
            f"{category:<15} "
            f"{category_correct:>2}/"
            f"{len(category_results):<2} "
            f"({category_accuracy * 100:.2f}%)"
        )

    print_confusion_matrix(results)

    print("\n")
    print("=" * 90)
    print("TEST COMPLETE")
    print("=" * 90)


if __name__ == "__main__":
    main()