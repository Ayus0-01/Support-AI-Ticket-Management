import json
from pathlib import Path
from collections import Counter, defaultdict


BASE_DIR = Path(__file__).resolve().parent

MIGRATED_PATH = (
    BASE_DIR / "category_seed_data_migrated.json"
)

RESOLVED_PATH = (
    BASE_DIR / "resolved_review_tickets.json"
)


def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main():
    migrated = load_json(MIGRATED_PATH)
    resolved = load_json(RESOLVED_PATH)

    tickets = (
        migrated["tickets"]
        + resolved["tickets"]
    )

    category_counts = Counter(
        ticket["category"]
        for ticket in tickets
    )

    subcategory_counts = defaultdict(Counter)

    for ticket in tickets:
        category = ticket["category"]
        subcategory = ticket.get(
            "subcategory"
        )

        if subcategory is not None:
            subcategory_counts[
                category
            ][subcategory] += 1

    print("=" * 90)
    print("MIGRATED DATASET DISTRIBUTION AUDIT")
    print("=" * 90)

    print(
        f"\nTotal tickets: {len(tickets)}"
    )

    print("\nCATEGORY DISTRIBUTION")
    print("-" * 90)

    for category, count in sorted(
        category_counts.items()
    ):
        percentage = (
            count / len(tickets)
        ) * 100

        print(
            f"{category:20} "
            f"{count:5} "
            f"({percentage:6.2f}%)"
        )

    print("\nSUBCATEGORY DISTRIBUTION")
    print("-" * 90)

    for category in sorted(
        subcategory_counts
    ):
        print(
            f"\n[{category}]"
        )

        for (
            subcategory,
            count,
        ) in sorted(
            subcategory_counts[
                category
            ].items()
        ):
            print(
                f"  {subcategory:30} "
                f"{count:5}"
            )

    print("\n" + "=" * 90)
    print("UNCLASSIFIED CHECK")
    print("=" * 90)

    unclassified = category_counts.get(
        "UNCLASSIFIED",
        0,
    )

    print(
        f"UNCLASSIFIED examples: "
        f"{unclassified}"
    )

    if unclassified:
        percentage = (
            unclassified / len(tickets)
        ) * 100

        print(
            f"UNCLASSIFIED percentage: "
            f"{percentage:.2f}%"
        )

    print("\n" + "=" * 90)


if __name__ == "__main__":
    main()