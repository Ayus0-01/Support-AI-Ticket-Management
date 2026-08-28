import json
from pathlib import Path
from collections import Counter


BASE_DIR = Path(__file__).resolve().parent

REVIEW_PATH = (
    BASE_DIR / "taxonomy_review_queue.json"
)

OUTPUT_PATH = (
    BASE_DIR / "taxonomy_review_report.json"
)


APPROVED_CATEGORIES = {
    "NETWORK",
    "VPN",
    "ACCESS",
    "SOFTWARE",
    "HARDWARE",
    "PRINTER",
    "EMAIL",
    "SECURITY",
    "APPLICATION",
    "UNCLASSIFIED",
}


def load_review_queue():
    with open(
        REVIEW_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main():
    data = load_review_queue()

    tickets = data["tickets"]

    grouped = {}

    for ticket in tickets:

        key = (
            ticket["source_category"],
            ticket["source_subcategory"],
        )

        grouped.setdefault(
            key,
            [],
        ).append(ticket)

    report = []

    for group, group_tickets in sorted(
        grouped.items()
    ):

        source_category, source_subcategory = group

        print("\n" + "=" * 100)
        print(
            f"{source_category} / "
            f"{source_subcategory}"
        )
        print(
            f"Tickets: {len(group_tickets)}"
        )
        print("=" * 100)

        report_group = {
            "source_category": source_category,
            "source_subcategory": source_subcategory,
            "tickets": [],
        }

        for index, ticket in enumerate(
            group_tickets,
            start=1,
        ):

            print(
                f"\n[{index}] "
                f"{ticket['subject']}"
            )

            print(
                f"    {ticket['description']}"
            )

            report_group["tickets"].append(
                {
                    "subject": ticket["subject"],
                    "description": ticket["description"],
                    "recommended_category": None,
                    "recommended_subcategory": None,
                    "review_status": "PENDING",
                }
            )

        report.append(report_group)

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            {
                "approved_categories": sorted(
                    APPROVED_CATEGORIES
                ),
                "groups": report,
            },
            file,
            indent=2,
            ensure_ascii=False,
        )

    counts = Counter(
        (
            ticket["source_category"],
            ticket["source_subcategory"],
        )
        for ticket in tickets
    )

    print("\n" + "=" * 100)
    print("REVIEW QUEUE SUMMARY")
    print("=" * 100)

    for group, count in sorted(
        counts.items()
    ):
        print(
            f"{group[0]:15} / "
            f"{group[1]:25} "
            f"{count}"
        )

    print(
        f"\nTotal review tickets: "
        f"{len(tickets)}"
    )

    print(
        f"Report written to: "
        f"{OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()