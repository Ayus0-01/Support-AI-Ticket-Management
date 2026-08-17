import json
from collections import Counter
from pathlib import Path


DATASET_PATH = Path(__file__).parent / "category_seed_data.json"


def main():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    tickets = data["tickets"]

    category_counts = Counter(
        ticket["category"]
        for ticket in tickets
    )

    subcategory_counts = Counter(
        (
            ticket["category"],
            ticket["subcategory"]
        )
        for ticket in tickets
    )

    print("\nCATEGORY DISTRIBUTION")
    print("=" * 30)

    for category, count in sorted(category_counts.items()):
        print(f"{category:15} {count}")

    print("\nSUBCATEGORY DISTRIBUTION")
    print("=" * 40)

    for (category, subcategory), count in sorted(
        subcategory_counts.items()
    ):
        print(
            f"{category:15} | "
            f"{subcategory:25} | "
            f"{count}"
        )

    print("\nTOTAL:", len(tickets))


if __name__ == "__main__":
    main()