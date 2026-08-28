import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

MIGRATED_PATH = (
    BASE_DIR / "category_seed_data_migrated.json"
)

RESOLVED_PATH = (
    BASE_DIR / "resolved_review_tickets.json"
)

OUTPUT_PATH = (
    BASE_DIR / "category_seed_data_v2.json"
)


from add_access_examples import ACCESS_EXAMPLES
from add_network_examples import NETWORK_EXAMPLES
from add_vpn_examples import VPN_EXAMPLES
from add_hardware_examples import HARDWARE_EXAMPLES
from add_email_examples import EMAIL_EXAMPLES
from add_security_examples import SECURITY_EXAMPLES
from add_application_examples import APPLICATION_EXAMPLES
from add_printer_examples import PRINTER_EXAMPLES


EMAIL_SPAM_EXAMPLES = [
    {
        "subject": "Large volume of spam emails",
        "description": "My company mailbox is receiving a large number of unsolicited marketing messages.",
        "category": "EMAIL",
        "subcategory": "Spam",
    },
    {
        "subject": "Unwanted messages in mailbox",
        "description": "My work inbox is receiving repeated unwanted messages from unknown senders.",
        "category": "EMAIL",
        "subcategory": "Spam",
    },
    {
        "subject": "Spam messages flooding inbox",
        "description": "A large number of unwanted emails are filling my company mailbox.",
        "category": "EMAIL",
        "subcategory": "Spam",
    },
    {
        "subject": "Junk email problem",
        "description": "My corporate mailbox is receiving a high volume of unsolicited junk email.",
        "category": "EMAIL",
        "subcategory": "Spam",
    },
    {
        "subject": "Too many unwanted emails",
        "description": "I am receiving many unsolicited messages in my work inbox.",
        "category": "EMAIL",
        "subcategory": "Spam",
    },
    {
        "subject": "Mailbox receiving junk mail",
        "description": "My company mailbox is being flooded with unwanted messages.",
        "category": "EMAIL",
        "subcategory": "Spam",
    },
    {
        "subject": "Unsolicited email issue",
        "description": "I am receiving repeated unsolicited emails in my work mailbox.",
        "category": "EMAIL",
        "subcategory": "Spam",
    },
    {
        "subject": "Spam volume increased",
        "description": "The amount of unwanted email reaching my company mailbox has increased significantly.",
        "category": "EMAIL",
        "subcategory": "Spam",
    },
    {
        "subject": "Junk messages appearing in inbox",
        "description": "My work inbox contains a large number of unwanted messages.",
        "category": "EMAIL",
        "subcategory": "Spam",
    },
    {
        "subject": "Unwanted email flood",
        "description": "My corporate inbox is being flooded with unsolicited email.",
        "category": "EMAIL",
        "subcategory": "Spam",
    },
    {
        "subject": "Spam reaching company mailbox",
        "description": "A large amount of junk email is reaching my company mailbox.",
        "category": "EMAIL",
        "subcategory": "Spam",
    },
    {
        "subject": "Repeated junk email",
        "description": "My work mailbox keeps receiving repeated unsolicited messages.",
        "category": "EMAIL",
        "subcategory": "Spam",
    },
    {
        "subject": "Unwanted email messages",
        "description": "I am receiving unwanted messages regularly in my corporate inbox.",
        "category": "EMAIL",
        "subcategory": "Spam",
    },
    {
        "subject": "Mailbox spam problem",
        "description": "My company mailbox is receiving excessive amounts of unsolicited email.",
        "category": "EMAIL",
        "subcategory": "Spam",
    },
    {
        "subject": "Junk mail filling inbox",
        "description": "Unwanted emails are filling my work mailbox and making it difficult to manage.",
        "category": "EMAIL",
        "subcategory": "Spam",
    },
]


def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def make_key(ticket):
    return (
        ticket["subject"].strip().lower(),
        ticket["description"].strip().lower(),
        ticket["category"],
        ticket.get("subcategory"),
    )


def main():
    migrated = load_json(
        MIGRATED_PATH
    )

    resolved = load_json(
        RESOLVED_PATH
    )

    base_tickets = (
        migrated["tickets"]
        + resolved["tickets"]
    )

    if len(base_tickets) != 502:
        raise ValueError(
            "Expected exactly 502 corrected base tickets."
        )

    expansion_groups = [
        ACCESS_EXAMPLES,
        NETWORK_EXAMPLES,
        VPN_EXAMPLES,
        HARDWARE_EXAMPLES,
        EMAIL_EXAMPLES,
        EMAIL_SPAM_EXAMPLES,
        SECURITY_EXAMPLES,
        APPLICATION_EXAMPLES,
        PRINTER_EXAMPLES,
    ]

    final_tickets = list(base_tickets)

    existing_keys = {
        make_key(ticket)
        for ticket in final_tickets
    }

    for group in expansion_groups:

        for ticket in group:

            key = make_key(ticket)

            if key in existing_keys:
                raise ValueError(
                    "Duplicate example detected:\n"
                    f"{ticket}"
                )

            final_tickets.append(ticket)
            existing_keys.add(key)

    expected_total = (
        502
        + 54
        + 36
        + 36
        + 54
        + 36
        + 15
        + 36
        + 72
        + 90
    )

    if len(final_tickets) != expected_total:
        raise ValueError(
            f"Unexpected final size: "
            f"{len(final_tickets)} "
            f"(expected {expected_total})"
        )

    output = {
        "taxonomy_version": "v2",
        "source_taxonomy_version": "v1",
        "tickets": final_tickets,
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
    print("FINAL V2 DATASET CREATED")
    print("=" * 90)

    print(
        "Base tickets:",
        len(base_tickets),
    )

    print(
        "Final tickets:",
        len(final_tickets),
    )

    print(
        "Output:",
        OUTPUT_PATH,
    )

    print(
        "\nOriginal datasets were NOT modified."
    )


if __name__ == "__main__":
    main()