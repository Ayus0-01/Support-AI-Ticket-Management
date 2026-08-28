import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

SOURCE_PATH = (
    BASE_DIR / "category_seed_data_hardware_expanded.json"
)

OUTPUT_PATH = (
    BASE_DIR / "category_seed_data_email_expanded.json"
)


EMAIL_EXAMPLES = [
    # -------------------------------------------------
    # DISTRIBUTION LIST
    # -------------------------------------------------

    {
        "subject": "Distribution list access problem",
        "description": "I am not receiving messages sent to the team distribution list.",
        "category": "EMAIL",
        "subcategory": "Distribution list",
    },
    {
        "subject": "Add user to distribution list",
        "description": "Please add me to the distribution list for my department.",
        "category": "EMAIL",
        "subcategory": "Distribution list",
    },
    {
        "subject": "Distribution list membership request",
        "description": "I need to be added to the appropriate team email distribution list.",
        "category": "EMAIL",
        "subcategory": "Distribution list",
    },
    {
        "subject": "Team mailing list not receiving emails",
        "description": "Messages sent to our team distribution list are not reaching my mailbox.",
        "category": "EMAIL",
        "subcategory": "Distribution list",
    },
    {
        "subject": "Remove user from distribution list",
        "description": "Please remove me from a distribution list I no longer need.",
        "category": "EMAIL",
        "subcategory": "Distribution list",
    },
    {
        "subject": "Distribution list membership issue",
        "description": "My account appears to be missing from the required department distribution list.",
        "category": "EMAIL",
        "subcategory": "Distribution list",
    },
    {
        "subject": "Department mailing list request",
        "description": "Please add my account to the distribution list used by my department.",
        "category": "EMAIL",
        "subcategory": "Distribution list",
    },
    {
        "subject": "Distribution group not delivering mail",
        "description": "Emails sent through the team distribution group are not reaching all members.",
        "category": "EMAIL",
        "subcategory": "Distribution list",
    },
    {
        "subject": "Cannot receive distribution list messages",
        "description": "I am not receiving messages addressed to the company distribution list.",
        "category": "EMAIL",
        "subcategory": "Distribution list",
    },
    {
        "subject": "Join project mailing list",
        "description": "Please add me to the distribution list for the project I am working on.",
        "category": "EMAIL",
        "subcategory": "Distribution list",
    },
    {
        "subject": "Distribution list update request",
        "description": "Please update my membership in the team distribution list.",
        "category": "EMAIL",
        "subcategory": "Distribution list",
    },
    {
        "subject": "Mailing list access request",
        "description": "I need access to the distribution list used by my team.",
        "category": "EMAIL",
        "subcategory": "Distribution list",
    },
    {
        "subject": "Distribution group membership missing",
        "description": "My account is not included in the required department mailing group.",
        "category": "EMAIL",
        "subcategory": "Distribution list",
    },
    {
        "subject": "Distribution list message delivery issue",
        "description": "Messages sent to the distribution list are not appearing in my inbox.",
        "category": "EMAIL",
        "subcategory": "Distribution list",
    },
    {
        "subject": "Request distribution list membership",
        "description": "I need to be included in the mailing list for my department.",
        "category": "EMAIL",
        "subcategory": "Distribution list",
    },
    {
        "subject": "Team distribution list problem",
        "description": "The team distribution list is not delivering messages correctly.",
        "category": "EMAIL",
        "subcategory": "Distribution list",
    },
    {
        "subject": "Distribution list subscription request",
        "description": "Please subscribe my company account to the appropriate distribution list.",
        "category": "EMAIL",
        "subcategory": "Distribution list",
    },
    {
        "subject": "Distribution list membership change",
        "description": "I need my membership changed for an internal distribution list.",
        "category": "EMAIL",
        "subcategory": "Distribution list",
    },

    # -------------------------------------------------
    # STORAGE QUOTA
    # -------------------------------------------------

    {
        "subject": "Mailbox storage quota exceeded",
        "description": "My mailbox has reached its storage limit and I cannot send new email.",
        "category": "EMAIL",
        "subcategory": "Storage quota",
    },
    {
        "subject": "Email storage full",
        "description": "My company mailbox is full and has reached the allowed storage quota.",
        "category": "EMAIL",
        "subcategory": "Storage quota",
    },
    {
        "subject": "Mailbox quota warning",
        "description": "I received a warning that my mailbox is approaching its storage limit.",
        "category": "EMAIL",
        "subcategory": "Storage quota",
    },
    {
        "subject": "Cannot send email due to mailbox limit",
        "description": "My mailbox storage quota has been exceeded and outgoing email is failing.",
        "category": "EMAIL",
        "subcategory": "Storage quota",
    },
    {
        "subject": "Mailbox storage limit reached",
        "description": "My work mailbox has reached the maximum allowed storage capacity.",
        "category": "EMAIL",
        "subcategory": "Storage quota",
    },
    {
        "subject": "Email account storage problem",
        "description": "My company email account is running out of storage space.",
        "category": "EMAIL",
        "subcategory": "Storage quota",
    },
    {
        "subject": "Mailbox quota exceeded",
        "description": "The mailbox quota has been exceeded and I am unable to send messages.",
        "category": "EMAIL",
        "subcategory": "Storage quota",
    },
    {
        "subject": "Need mailbox storage cleanup",
        "description": "My mailbox is almost full and I need help dealing with the storage quota.",
        "category": "EMAIL",
        "subcategory": "Storage quota",
    },
    {
        "subject": "Mailbox is over storage limit",
        "description": "My corporate mailbox has exceeded its configured storage limit.",
        "category": "EMAIL",
        "subcategory": "Storage quota",
    },
    {
        "subject": "Email storage capacity reached",
        "description": "I cannot send new messages because my mailbox storage capacity has been reached.",
        "category": "EMAIL",
        "subcategory": "Storage quota",
    },
    {
        "subject": "Mailbox storage warning",
        "description": "The system is warning that my mailbox is close to its storage quota.",
        "category": "EMAIL",
        "subcategory": "Storage quota",
    },
    {
        "subject": "Corporate mailbox full",
        "description": "My company mailbox is full and needs space before I can continue sending email.",
        "category": "EMAIL",
        "subcategory": "Storage quota",
    },
    {
        "subject": "Storage quota issue on mailbox",
        "description": "I am experiencing problems because my mailbox has reached its storage quota.",
        "category": "EMAIL",
        "subcategory": "Storage quota",
    },
    {
        "subject": "Mailbox cannot accept more email",
        "description": "My mailbox has reached its storage limit and cannot accept additional messages.",
        "category": "EMAIL",
        "subcategory": "Storage quota",
    },
    {
        "subject": "Work email storage limit",
        "description": "The storage limit for my work mailbox has been reached.",
        "category": "EMAIL",
        "subcategory": "Storage quota",
    },
    {
        "subject": "Mailbox capacity problem",
        "description": "My corporate mailbox is nearing or exceeding its storage capacity.",
        "category": "EMAIL",
        "subcategory": "Storage quota",
    },
    {
        "subject": "Email quota exceeded",
        "description": "My mailbox quota has been exceeded and email operations are being affected.",
        "category": "EMAIL",
        "subcategory": "Storage quota",
    },
    {
        "subject": "Mailbox storage management request",
        "description": "I need help because my work mailbox has reached its permitted storage quota.",
        "category": "EMAIL",
        "subcategory": "Storage quota",
    },
]


def main():
    with open(
        SOURCE_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    existing = data["tickets"]

    print(
        "Existing tickets:",
        len(existing),
    )

    print(
        "New EMAIL examples:",
        len(EMAIL_EXAMPLES),
    )

    if len(EMAIL_EXAMPLES) != 36:
        raise ValueError(
            "Expected exactly 36 EMAIL examples."
        )

    existing_keys = {
        (
            ticket["subject"].strip().lower(),
            ticket["description"].strip().lower(),
        )
        for ticket in existing
    }

    duplicate_examples = [
        example
        for example in EMAIL_EXAMPLES
        if (
            example["subject"].strip().lower(),
            example["description"].strip().lower(),
        )
        in existing_keys
    ]

    if duplicate_examples:
        raise ValueError(
            "Duplicate EMAIL examples found."
        )

    new_tickets = existing + EMAIL_EXAMPLES

    output = {
        "taxonomy_version": "v2",
        "source_taxonomy_version": data.get(
            "source_taxonomy_version"
        ),
        "taxonomy": data.get(
            "taxonomy",
            []
        ),
        "tickets": new_tickets,
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

    print(
        "\nEMAIL EXPANSION COMPLETE"
    )

    print(
        "Total tickets:",
        len(new_tickets),
    )

    print(
        "EMAIL total:",
        sum(
            ticket["category"] == "EMAIL"
            for ticket in new_tickets
        ),
    )

    print(
        "Output:",
        OUTPUT_PATH,
    )

    print(
        "\nOriginal HARDWARE-expanded dataset "
        "was NOT modified."
    )


if __name__ == "__main__":
    main()