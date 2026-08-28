import json
from pathlib import Path
from collections import Counter


BASE_DIR = Path(__file__).resolve().parent


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


def load_json(filename):
    path = BASE_DIR / filename

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def audit_category_dataset():
    data = load_json("category_seed_data.json")
    tickets = data["tickets"]

    print("=" * 90)
    print("CATEGORY / SUBCATEGORY TAXONOMY AUDIT")
    print("=" * 90)

    print(f"\nTotal tickets: {len(tickets)}")

    actual_categories = sorted(
        {
            ticket.get("category", "")
            for ticket in tickets
        }
    )

    actual_category_counts = Counter(
        ticket.get("category", "")
        for ticket in tickets
    )

    print("\nACTUAL CATEGORIES")
    print("-" * 90)

    for category in actual_categories:
        print(
            f"{category:20} "
            f"{actual_category_counts[category]:5} examples"
        )

    approved_categories = set(
        APPROVED_TAXONOMY.keys()
    )

    missing_categories = sorted(
        approved_categories - set(actual_categories)
    )

    unexpected_categories = sorted(
        set(actual_categories) - approved_categories
    )

    print("\nMISSING APPROVED CATEGORIES")
    print("-" * 90)

    if missing_categories:
        for category in missing_categories:
            print(category)
    else:
        print("NONE")

    print("\nUNEXPECTED / OLD CATEGORIES")
    print("-" * 90)

    if unexpected_categories:
        for category in unexpected_categories:
            print(category)
    else:
        print("NONE")

    print("\nSUBCATEGORY AUDIT")
    print("-" * 90)

    all_mismatches = False

    for category in sorted(APPROVED_TAXONOMY):

        expected = APPROVED_TAXONOMY[category]

        actual = {
            ticket.get("subcategory", "")
            for ticket in tickets
            if ticket.get("category") == category
        }

        counts = Counter(
            ticket.get("subcategory", "")
            for ticket in tickets
            if ticket.get("category") == category
        )

        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)

        print(f"\n[{category}]")

        print("Actual labels:")
        if actual:
            for label in sorted(actual):
                print(
                    f"  {label:30} "
                    f"{counts[label]:5}"
                )
        else:
            print("  NONE")

        print("Missing approved labels:")
        if missing:
            all_mismatches = True
            for label in missing:
                print(f"  {label}")
        else:
            print("  NONE")

        print("Unexpected / old labels:")
        if unexpected:
            all_mismatches = True
            for label in unexpected:
                print(f"  {label}")
        else:
            print("  NONE")

    print("\n" + "=" * 90)
    print("AUDIT SUMMARY")
    print("=" * 90)

    print(
        f"Approved categories: "
        f"{len(approved_categories)}"
    )

    print(
        f"Actual categories:   "
        f"{len(actual_categories)}"
    )

    print(
        f"Missing categories:  "
        f"{len(missing_categories)}"
    )

    print(
        f"Unexpected categories:"
        f" {len(unexpected_categories)}"
    )

    print(
        f"Taxonomy mismatches: "
        f"{'YES' if all_mismatches or missing_categories or unexpected_categories else 'NO'}"
    )


if __name__ == "__main__":
    audit_category_dataset()