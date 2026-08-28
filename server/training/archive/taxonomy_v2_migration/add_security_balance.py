import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

SOURCE_PATH = (
    BASE_DIR / "category_seed_data_v2_curated.json"
)

OUTPUT_PATH = (
    BASE_DIR / "category_seed_data_v2_final.json"
)


SECURITY_BALANCE_EXAMPLES = [
    # -------------------------------------------------
    # PHISHING REPORT — 7
    # -------------------------------------------------

    {
        "subject": "Report suspected phishing email",
        "description": "I received an email that appears to be a phishing attempt and want to report it.",
        "category": "SECURITY",
        "subcategory": "Phishing report",
    },
    {
        "subject": "Phishing email needs reporting",
        "description": "A suspicious email is attempting to collect credentials and I need to report it.",
        "category": "SECURITY",
        "subcategory": "Phishing report",
    },
    {
        "subject": "Report credential phishing attempt",
        "description": "I received a message that appears to be trying to steal my company login credentials.",
        "category": "SECURITY",
        "subcategory": "Phishing report",
    },
    {
        "subject": "Suspected phishing message",
        "description": "I believe an email I received is a phishing message and would like to report it.",
        "category": "SECURITY",
        "subcategory": "Phishing report",
    },
    {
        "subject": "Phishing incident report",
        "description": "Please record this suspicious email as a possible phishing incident.",
        "category": "SECURITY",
        "subcategory": "Phishing report",
    },
    {
        "subject": "Report malicious login email",
        "description": "An email is asking me to verify my credentials through a suspicious link.",
        "category": "SECURITY",
        "subcategory": "Phishing report",
    },
    {
        "subject": "Possible credential theft email",
        "description": "I received an email that appears to be attempting to steal company account information.",
        "category": "SECURITY",
        "subcategory": "Phishing report",
    },

    # -------------------------------------------------
    # SUSPICIOUS ACTIVITY — 14
    # -------------------------------------------------

    {
        "subject": "Suspicious activity on company laptop",
        "description": "My company laptop is behaving unexpectedly and I suspect suspicious activity.",
        "category": "SECURITY",
        "subcategory": "Suspicious activity",
    },
    {
        "subject": "Unexpected security activity",
        "description": "I noticed unusual activity on my work computer that I cannot explain.",
        "category": "SECURITY",
        "subcategory": "Suspicious activity",
    },
    {
        "subject": "Unusual login activity",
        "description": "There are login attempts on my corporate account that I do not recognize.",
        "category": "SECURITY",
        "subcategory": "Suspicious activity",
    },
    {
        "subject": "Unknown activity on workstation",
        "description": "My workstation is showing activity that I did not initiate.",
        "category": "SECURITY",
        "subcategory": "Suspicious activity",
    },
    {
        "subject": "Suspicious account behavior",
        "description": "I noticed unusual behavior on my company account and want it investigated.",
        "category": "SECURITY",
        "subcategory": "Suspicious activity",
    },
    {
        "subject": "Unrecognized system activity",
        "description": "There is unexpected activity on my corporate device that appears suspicious.",
        "category": "SECURITY",
        "subcategory": "Suspicious activity",
    },
    {
        "subject": "Possible unauthorized activity",
        "description": "I noticed activity on my work account that may not have been authorized by me.",
        "category": "SECURITY",
        "subcategory": "Suspicious activity",
    },
    {
        "subject": "Suspicious access detected",
        "description": "An unusual access event was recorded on my company account.",
        "category": "SECURITY",
        "subcategory": "Suspicious activity",
    },
    {
        "subject": "Unknown process running",
        "description": "An unfamiliar process is running on my company workstation and appears suspicious.",
        "category": "SECURITY",
        "subcategory": "Suspicious activity",
    },
    {
        "subject": "Unexpected changes on work computer",
        "description": "Settings on my company computer changed unexpectedly without my action.",
        "category": "SECURITY",
        "subcategory": "Suspicious activity",
    },
    {
        "subject": "Unusual account activity",
        "description": "My corporate account shows activity that I do not recognize.",
        "category": "SECURITY",
        "subcategory": "Suspicious activity",
    },
    {
        "subject": "Suspicious device behavior",
        "description": "My company-issued device is behaving in an unusual and potentially suspicious way.",
        "category": "SECURITY",
        "subcategory": "Suspicious activity",
    },
    {
        "subject": "Unrecognized security event",
        "description": "A security event associated with my account is unfamiliar to me.",
        "category": "SECURITY",
        "subcategory": "Suspicious activity",
    },
    {
        "subject": "Possible unauthorized system activity",
        "description": "I found unusual system activity on my workstation that I did not initiate.",
        "category": "SECURITY",
        "subcategory": "Suspicious activity",
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
        "New SECURITY balance examples:",
        len(SECURITY_BALANCE_EXAMPLES),
    )

    if len(SECURITY_BALANCE_EXAMPLES) != 21:
        raise ValueError(
            "Expected exactly 21 SECURITY balance examples."
        )

    existing_keys = {
        (
            ticket["subject"].strip().lower(),
            ticket["description"].strip().lower(),
            ticket["category"],
            ticket.get("subcategory"),
        )
        for ticket in existing
    }

    for example in SECURITY_BALANCE_EXAMPLES:
        key = (
            example["subject"].strip().lower(),
            example["description"].strip().lower(),
            example["category"],
            example["subcategory"],
        )

        if key in existing_keys:
            raise ValueError(
                "Duplicate SECURITY example detected:\n"
                f"{example}"
            )

    new_tickets = (
        existing + SECURITY_BALANCE_EXAMPLES
    )

    output = {
        "taxonomy_version": "v2",
        "source_taxonomy_version": "v1",
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
        "\nSECURITY BALANCE COMPLETE"
    )

    print(
        "Total tickets:",
        len(new_tickets),
    )

    print(
        "Output:",
        OUTPUT_PATH,
    )

    print(
        "\nOriginal curated dataset was NOT modified."
    )


if __name__ == "__main__":
    main()