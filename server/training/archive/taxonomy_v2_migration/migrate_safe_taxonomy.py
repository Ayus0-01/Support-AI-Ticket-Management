import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

SOURCE_PATH = BASE_DIR / "category_seed_data.json"

MIGRATED_PATH = (
    BASE_DIR / "category_seed_data_migrated.json"
)

REVIEW_PATH = (
    BASE_DIR / "taxonomy_review_queue.json"
)


APPROVED_TAXONOMY = {
    "NETWORK": [
        "Connectivity",
        "WiFi",
        "LAN",
        "DNS",
        "Bandwidth",
    ],
    "VPN": [
        "Connection failure",
        "Certificate",
        "Client install",
        "Timeout",
    ],
    "ACCESS": [
        "Password reset",
        "Account lockout",
        "Permissions",
        "MFA",
        "Onboarding",
    ],
    "SOFTWARE": [
        "Installation",
        "Licensing",
        "Crash",
        "Update",
        "Compatibility",
    ],
    "HARDWARE": [
        "Laptop",
        "Desktop",
        "Peripheral",
        "Docking station",
        "Mobile device",
    ],
    "PRINTER": [
        "Not printing",
        "Driver",
        "Queue stuck",
        "Quality",
        "Scan",
    ],
    "EMAIL": [
        "Mailbox",
        "Distribution list",
        "Spam",
        "Calendar",
        "Storage quota",
    ],
    "SECURITY": [
        "Phishing report",
        "Malware",
        "Suspicious activity",
        "Data request",
    ],
    "APPLICATION": [
        "ERP",
        "CRM",
        "Internal tool",
        "Integration failure",
        "Performance",
    ],
    "UNCLASSIFIED": [],
}


# These are safe migrations based on the semantics
# of the existing examples.
SAFE_RENAMES = {
    ("NETWORK", "DNS resolution"):
        ("NETWORK", "DNS"),

    ("VPN", "Certificate issue"):
        ("VPN", "Certificate"),

    ("APPLICATION", "Error/crash"):
        ("SOFTWARE", "Crash"),

    ("EMAIL", "Calendar sync"):
        ("EMAIL", "Calendar"),

    ("HARDWARE", "Monitor"):
        ("HARDWARE", "Peripheral"),

    ("SOFTWARE", "Update/patch"):
        ("SOFTWARE", "Update"),

    # Already-valid labels are intentionally included
    # so the migrated dataset has consistent labels.
    ("NETWORK", "Connectivity"):
        ("NETWORK", "Connectivity"),

    ("NETWORK", "Bandwidth"):
        ("NETWORK", "Bandwidth"),

    ("VPN", "Connection failure"):
        ("VPN", "Connection failure"),

    ("ACCESS", "Account lockout"):
        ("ACCESS", "Account lockout"),

    ("ACCESS", "Permissions"):
        ("ACCESS", "Permissions"),

    ("APPLICATION", "Performance"):
        ("APPLICATION", "Performance"),

    ("EMAIL", "Mailbox"):
        ("EMAIL", "Mailbox"),

    ("HARDWARE", "Laptop"):
        ("HARDWARE", "Laptop"),

    ("HARDWARE", "Peripheral"):
        ("HARDWARE", "Peripheral"),

    ("SOFTWARE", "Installation"):
        ("SOFTWARE", "Installation"),

    ("SOFTWARE", "Licensing"):
        ("SOFTWARE", "Licensing"),

    ("SOFTWARE", "Compatibility"):
        ("SOFTWARE", "Compatibility"),
}


# These groups cannot safely be migrated without
# examining the individual ticket.
MANUAL_REVIEW = {
    ("ACCESS", "New access request"),
    ("ACCESS", "Role change"),

    ("APPLICATION", "Authentication"),
    ("APPLICATION", "Feature request"),

    ("EMAIL", "Attachment issue"),
    ("EMAIL", "Spam/phishing"),

    ("HARDWARE", "Replacement"),

    ("NETWORK", "Firewall rules"),

    ("VPN", "Slow connection"),
    ("VPN", "Split tunneling"),
}


def load_source():
    with open(
        SOURCE_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def build_categories():
    return [
        {
            "name": category,
            "subcategories": subcategories,
        }
        for category, subcategories
        in APPROVED_TAXONOMY.items()
    ]


def main():
    data = load_source()

    source_tickets = data["tickets"]

    migrated_tickets = []
    review_tickets = []

    for ticket in source_tickets:

        source_category = ticket.get(
            "category"
        )

        source_subcategory = ticket.get(
            "subcategory"
        )

        source_key = (
            source_category,
            source_subcategory,
        )

        if source_key in SAFE_RENAMES:

            target_category, target_subcategory = (
                SAFE_RENAMES[source_key]
            )

            migrated_ticket = ticket.copy()

            migrated_ticket["category"] = (
                target_category
            )

            migrated_ticket["subcategory"] = (
                target_subcategory
            )

            migrated_tickets.append(
                migrated_ticket
            )

        elif source_key in MANUAL_REVIEW:

            review_ticket = ticket.copy()

            review_ticket["review_status"] = (
                "PENDING"
            )

            review_ticket["review_reason"] = (
                "Old taxonomy label requires "
                "individual semantic review."
            )

            review_ticket["source_category"] = (
                source_category
            )

            review_ticket["source_subcategory"] = (
                source_subcategory
            )

            review_ticket["recommended_category"] = (
                None
            )

            review_ticket["recommended_subcategory"] = (
                None
            )

            review_tickets.append(
                review_ticket
            )

        else:

            raise ValueError(
                "Unexpected training label found: "
                f"{source_category}/"
                f"{source_subcategory}"
            )

    migrated_data = {
        "taxonomy_version": "v2",
        "taxonomy": build_categories(),
        "source_taxonomy_version": data.get(
            "taxonomy_version"
        ),
        "migration_note": (
            "Safe migrations only. "
            "Manual-review tickets are excluded "
            "until individually classified."
        ),
        "tickets": migrated_tickets,
    }

    review_data = {
        "taxonomy_version": "v2",
        "source_taxonomy_version": data.get(
            "taxonomy_version"
        ),
        "review_status": "PENDING",
        "tickets": review_tickets,
    }

    with open(
        MIGRATED_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            migrated_data,
            file,
            indent=2,
            ensure_ascii=False,
        )

    with open(
        REVIEW_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            review_data,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("=" * 90)
    print("SAFE TAXONOMY MIGRATION COMPLETE")
    print("=" * 90)

    print(
        f"Original tickets: "
        f"{len(source_tickets)}"
    )

    print(
        f"Safely migrated: "
        f"{len(migrated_tickets)}"
    )

    print(
        f"Manual review: "
        f"{len(review_tickets)}"
    )

    print(
        f"Total accounted for: "
        f"{len(migrated_tickets) + len(review_tickets)}"
    )

    print("\nCreated:")
    print(
        f"  {MIGRATED_PATH}"
    )
    print(
        f"  {REVIEW_PATH}"
    )

    print(
        "\nOriginal dataset was NOT modified."
    )


if __name__ == "__main__":
    main()