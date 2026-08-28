import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = (
    BASE_DIR / "category_seed_data_v2_deduped.json"
)


def main():
    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    tickets = [
        ticket
        for ticket in data["tickets"]
        if ticket["category"] == "UNCLASSIFIED"
    ]

    print("=" * 100)
    print("UNCLASSIFIED REVIEW")
    print("=" * 100)
    print(
        f"Total UNCLASSIFIED tickets: {len(tickets)}"
    )

    for index, ticket in enumerate(
        tickets,
        start=1,
    ):
        print("\n" + "-" * 100)
        print(f"[{index}]")
        print(
            f"SUBJECT: {ticket['subject']}"
        )
        print(
            f"DESCRIPTION: {ticket['description']}"
        )


if __name__ == "__main__":
    main()