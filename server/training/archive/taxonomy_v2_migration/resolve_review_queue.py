import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

REVIEW_PATH = BASE_DIR / "taxonomy_review_queue.json"

OUTPUT_PATH = (
    BASE_DIR / "resolved_review_tickets.json"
)


def resolve_ticket(ticket):
    category = ticket["source_category"]
    subcategory = ticket["source_subcategory"]
    subject = ticket["subject"].lower()
    description = ticket["description"].lower()

    # -------------------------------------------------
    # ACCESS
    # -------------------------------------------------

    if (
        category == "ACCESS"
        and subcategory in {
            "New access request",
            "Role change",
        }
    ):
        return "UNCLASSIFIED", None

    # -------------------------------------------------
    # APPLICATION
    # -------------------------------------------------

    if (
        category == "APPLICATION"
        and subcategory == "Authentication"
    ):
        return "UNCLASSIFIED", None

    if (
        category == "APPLICATION"
        and subcategory == "Feature request"
    ):
        return "UNCLASSIFIED", None

    # -------------------------------------------------
    # EMAIL ATTACHMENTS
    # -------------------------------------------------

    if (
        category == "EMAIL"
        and subcategory == "Attachment issue"
    ):
        return "UNCLASSIFIED", None

    # -------------------------------------------------
    # EMAIL SPAM / PHISHING
    # -------------------------------------------------

    if (
        category == "EMAIL"
        and subcategory == "Spam/phishing"
    ):

        spam_keywords = {
            "spam email",
            "spam message",
            "unwanted email",
            "unwanted messages",
            "large amount of spam",
            "large number of unwanted",
        }

        if any(
            keyword in subject
            or keyword in description
            for keyword in spam_keywords
        ):
            return "EMAIL", "Spam"

        suspicious_activity_keywords = {
            "suspicious attachment",
            "malicious email",
            "malicious",
            "security concern",
        }

        if any(
            keyword in subject
            or keyword in description
            for keyword in suspicious_activity_keywords
        ):
            return "SECURITY", "Suspicious activity"

        return "SECURITY", "Phishing report"

    # -------------------------------------------------
    # HARDWARE REPLACEMENT
    # -------------------------------------------------

    if (
        category == "HARDWARE"
        and subcategory == "Replacement"
    ):

        if "laptop" in subject or "laptop" in description:
            return "HARDWARE", "Laptop"

        if (
            "monitor" in subject
            or "monitor" in description
            or "keyboard" in subject
            or "keyboard" in description
        ):
            return "HARDWARE", "Peripheral"

        return "UNCLASSIFIED", None

    # -------------------------------------------------
    # NETWORK FIREWALL
    # -------------------------------------------------

    if (
        category == "NETWORK"
        and subcategory == "Firewall rules"
    ):
        return "UNCLASSIFIED", None

    # -------------------------------------------------
    # VPN
    # -------------------------------------------------

    if category == "VPN":

        if subcategory == "Slow connection":
            return "UNCLASSIFIED", None

        if subcategory == "Split tunneling":
            return "UNCLASSIFIED", None

    raise ValueError(
        "Unresolved ticket: "
        f"{category}/{subcategory} - "
        f"{ticket['subject']}"
    )


def main():
    with open(
        REVIEW_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    resolved = []

    for ticket in data["tickets"]:

        new_category, new_subcategory = (
            resolve_ticket(ticket)
        )

        resolved_ticket = {
            "subject": ticket["subject"],
            "description": ticket["description"],
            "category": new_category,
            "subcategory": new_subcategory,
            "source_category": (
                ticket["source_category"]
            ),
            "source_subcategory": (
                ticket["source_subcategory"]
            ),
            "migration_status": "RESOLVED",
        }

        resolved.append(
            resolved_ticket
        )

    output = {
        "taxonomy_version": "v2",
        "source_taxonomy_version": "v1",
        "tickets": resolved,
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

    print("=" * 90)
    print("REVIEW QUEUE RESOLUTION COMPLETE")
    print("=" * 90)
    print(
        f"Resolved tickets: {len(resolved)}"
    )
    print(
        f"Output: {OUTPUT_PATH}"
    )
    print(
        "\nOriginal review queue was NOT modified."
    )


if __name__ == "__main__":
    main()