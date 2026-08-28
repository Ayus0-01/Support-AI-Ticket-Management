import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

INPUT_PATH = (
    BASE_DIR / "category_seed_data_v2.json"
)

OUTPUT_PATH = (
    BASE_DIR / "category_seed_data_v2_deduped.json"
)


DUPLICATES_TO_REMOVE_ONCE = {
    (
        "mailbox unavailable",
        "i cannot access my company mailbox.",
        "EMAIL",
        "Mailbox",
    ),
    (
        "update installation error",
        "an error appears when applying the software update.",
        "SOFTWARE",
        "Update",
    ),
}


def make_key(ticket):
    return (
        ticket["subject"].strip().lower(),
        ticket["description"].strip().lower(),
        ticket["category"],
        ticket.get("subcategory"),
    )


def main():
    with open(
        INPUT_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    tickets = data["tickets"]

    kept = []
    removed = set()

    for ticket in tickets:
        key = make_key(ticket)

        if key in DUPLICATES_TO_REMOVE_ONCE:
            if key not in removed:
                kept.append(ticket)
                removed.add(key)
            else:
                continue
        else:
            kept.append(ticket)

    if len(kept) != 929:
        raise ValueError(
            f"Expected 929 tickets after deduplication, "
            f"got {len(kept)}"
        )

    output = {
        "taxonomy_version": "v2",
        "source_taxonomy_version": "v1",
        "tickets": kept,
    }

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("FINAL DATASET DEDUPLICATED")
    print("Original:", len(tickets))
    print("Final:", len(kept))
    print("Removed:", len(tickets) - len(kept))
    print("Output:", OUTPUT_PATH)


if __name__ == "__main__":
    main()