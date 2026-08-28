import json
from pathlib import Path
from collections import Counter


BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = (
    BASE_DIR / "category_seed_data_v2_final.json"
)


APPROVED_TAXONOMY = {
    "NETWORK": {
        "Connectivity",
        "WiFi",
        "LAN",
        "DNS",
        "Bandwidth",
    },
    "VPN": {
        "Connection failure",
        "Certificate",
        "Client install",
        "Timeout",
    },
    "ACCESS": {
        "Password reset",
        "Account lockout",
        "Permissions",
        "MFA",
        "Onboarding",
    },
    "SOFTWARE": {
        "Installation",
        "Licensing",
        "Crash",
        "Update",
        "Compatibility",
    },
    "HARDWARE": {
        "Laptop",
        "Desktop",
        "Peripheral",
        "Docking station",
        "Mobile device",
    },
    "PRINTER": {
        "Not printing",
        "Driver",
        "Queue stuck",
        "Quality",
        "Scan",
    },
    "EMAIL": {
        "Mailbox",
        "Distribution list",
        "Spam",
        "Calendar",
        "Storage quota",
    },
    "SECURITY": {
        "Phishing report",
        "Malware",
        "Suspicious activity",
        "Data request",
    },
    "APPLICATION": {
        "ERP",
        "CRM",
        "Internal tool",
        "Integration failure",
        "Performance",
    },
    "UNCLASSIFIED": set(),
}


def main():
    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    tickets = data["tickets"]

    print("=" * 100)
    print("FINAL TAXONOMY AUDIT")
    print("=" * 100)

    print(
        f"\nTOTAL TICKETS: {len(tickets)}"
    )

    # --------------------------------------------
    # CATEGORY COUNTS
    # --------------------------------------------

    category_counts = Counter(
        ticket["category"]
        for ticket in tickets
    )

    print("\nCATEGORY DISTRIBUTION")
    print("-" * 100)

    for category in sorted(
        APPROVED_TAXONOMY
    ):
        count = category_counts.get(
            category,
            0,
        )

        percentage = (
            count / len(tickets) * 100
        )

        print(
            f"{category:20}"
            f"{count:5}"
            f" ({percentage:6.2f}%)"
        )

    # --------------------------------------------
    # SUBCATEGORY COUNTS
    # --------------------------------------------

    print("\nSUBCATEGORY DISTRIBUTION")
    print("-" * 100)

    for category in sorted(
        APPROVED_TAXONOMY
    ):

        expected = APPROVED_TAXONOMY[
            category
        ]

        actual = Counter(
            ticket.get("subcategory")
            for ticket in tickets
            if ticket["category"]
            == category
        )

        print(f"\n[{category}]")

        if not expected:
            print(
                f"  UNCLASSIFIED: "
                f"{category_counts.get(category, 0)}"
            )
            continue

        for subcategory in sorted(
            expected
        ):
            print(
                f"  {subcategory:25}"
                f"{actual.get(subcategory, 0):5}"
            )

    # --------------------------------------------
    # INVALID LABELS
    # --------------------------------------------

    invalid_categories = sorted(
        {
            ticket["category"]
            for ticket in tickets
        }
        - set(APPROVED_TAXONOMY)
    )

    invalid_subcategories = []

    for ticket in tickets:

        category = ticket["category"]

        subcategory = ticket.get(
            "subcategory"
        )

        if category not in APPROVED_TAXONOMY:
            continue

        if category == "UNCLASSIFIED":
            continue

        if (
            subcategory
            not in APPROVED_TAXONOMY[category]
        ):
            invalid_subcategories.append(
                (
                    category,
                    subcategory,
                )
            )

    print(
        "\nINVALID CATEGORIES"
    )
    print("-" * 100)

    if invalid_categories:
        for item in invalid_categories:
            print(item)
    else:
        print("NONE")

    print(
        "\nINVALID SUBCATEGORIES"
    )
    print("-" * 100)

    if invalid_subcategories:
        for item in sorted(
            set(invalid_subcategories)
        ):
            print(
                f"{item[0]} / {item[1]}"
            )
    else:
        print("NONE")

    # --------------------------------------------
    # DUPLICATES
    # --------------------------------------------

    keys = [
        (
            ticket["subject"]
            .strip()
            .lower(),
            ticket["description"]
            .strip()
            .lower(),
            ticket["category"],
            ticket.get("subcategory"),
        )
        for ticket in tickets
    ]

    duplicate_count = (
        len(keys) - len(set(keys))
    )

    print(
        "\nDUPLICATES"
    )
    print("-" * 100)

    print(
        f"Duplicate records: "
        f"{duplicate_count}"
    )

    # --------------------------------------------
    # UNCLASSIFIED
    # --------------------------------------------

    unclassified_count = (
        category_counts.get(
            "UNCLASSIFIED",
            0,
        )
    )

    unclassified_percentage = (
        unclassified_count
        / len(tickets)
        * 100
    )

    print(
        "\nUNCLASSIFIED"
    )
    print("-" * 100)

    print(
        f"Count: {unclassified_count}"
    )

    print(
        f"Percentage: "
        f"{unclassified_percentage:.2f}%"
    )

    print("\n" + "=" * 100)
    print("AUDIT COMPLETE")
    print("=" * 100)


if __name__ == "__main__":
    main()