import json
from pathlib import Path

from taxonomy_mapping import MANUAL_REVIEW


DATASET_PATH = Path(__file__).parent / "category_seed_data.json"


def load_dataset():
    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main():
    data = load_dataset()

    tickets = data["tickets"]

    print("=" * 100)
    print("MANUAL TAXONOMY REVIEW")
    print("=" * 100)

    for category, subcategory in sorted(
        MANUAL_REVIEW
    ):
        matching = [
            ticket
            for ticket in tickets
            if (
                ticket.get("category")
                == category
                and ticket.get("subcategory")
                == subcategory
            )
        ]

        print("\n")
        print("=" * 100)
        print(
            f"{category} / {subcategory}"
        )
        print(
            f"Tickets: {len(matching)}"
        )
        print("=" * 100)

        for index, ticket in enumerate(
            matching,
            start=1,
        ):
            print(
                f"\n[{index}]"
            )
            print(
                f"SUBJECT: "
                f"{ticket.get('subject', '')}"
            )
            print(
                f"DESCRIPTION: "
                f"{ticket.get('description', '')}"
            )


if __name__ == "__main__":
    main()