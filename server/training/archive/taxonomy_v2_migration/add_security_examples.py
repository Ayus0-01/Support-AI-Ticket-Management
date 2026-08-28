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
    BASE_DIR / "category_seed_data_security_expanded.json"
)


SECURITY_EXAMPLES = [
    # -------------------------------------------------
    # MALWARE
    # -------------------------------------------------

    {
        "subject": "Possible malware infection",
        "description": "My work computer is showing signs of a possible malware infection.",
        "category": "SECURITY",
        "subcategory": "Malware",
    },
    {
        "subject": "Malware detected on laptop",
        "description": "A security alert indicates that malware may have been detected on my company laptop.",
        "category": "SECURITY",
        "subcategory": "Malware",
    },
    {
        "subject": "Suspicious malware warning",
        "description": "My workstation displayed a warning that malicious software may be present.",
        "category": "SECURITY",
        "subcategory": "Malware",
    },
    {
        "subject": "Computer infected with malware",
        "description": "I believe my company computer has been infected with malware.",
        "category": "SECURITY",
        "subcategory": "Malware",
    },
    {
        "subject": "Malicious software detected",
        "description": "The endpoint security tool reported malicious software on my work device.",
        "category": "SECURITY",
        "subcategory": "Malware",
    },
    {
        "subject": "Malware alert on workstation",
        "description": "A malware alert appeared on my corporate workstation.",
        "category": "SECURITY",
        "subcategory": "Malware",
    },
    {
        "subject": "Potential malware infection",
        "description": "I suspect that malicious software has infected my company laptop.",
        "category": "SECURITY",
        "subcategory": "Malware",
    },
    {
        "subject": "Security software found malware",
        "description": "The endpoint protection software found what appears to be malware on my computer.",
        "category": "SECURITY",
        "subcategory": "Malware",
    },
    {
        "subject": "Malware incident report",
        "description": "I need to report a suspected malware incident on a company device.",
        "category": "SECURITY",
        "subcategory": "Malware",
    },
    {
        "subject": "Workstation showing malware symptoms",
        "description": "My company workstation is behaving suspiciously and I suspect malware.",
        "category": "SECURITY",
        "subcategory": "Malware",
    },
    {
        "subject": "Malicious program on corporate device",
        "description": "A malicious program may have been installed on my company computer.",
        "category": "SECURITY",
        "subcategory": "Malware",
    },
    {
        "subject": "Endpoint malware alert",
        "description": "The security system generated an alert for possible malware on my endpoint.",
        "category": "SECURITY",
        "subcategory": "Malware",
    },
    {
        "subject": "Malware infection concern",
        "description": "I am concerned that my work laptop may have been infected with malicious software.",
        "category": "SECURITY",
        "subcategory": "Malware",
    },
    {
        "subject": "Detected malicious software",
        "description": "Our security software detected suspicious malicious software on my workstation.",
        "category": "SECURITY",
        "subcategory": "Malware",
    },
    {
        "subject": "Possible virus on work computer",
        "description": "I suspect a malware or virus infection on my company computer.",
        "category": "SECURITY",
        "subcategory": "Malware",
    },
    {
        "subject": "Corporate device malware issue",
        "description": "There appears to be malicious software affecting my company-issued device.",
        "category": "SECURITY",
        "subcategory": "Malware",
    },
    {
        "subject": "Malware quarantine alert",
        "description": "The endpoint protection system quarantined a file that appears to contain malware.",
        "category": "SECURITY",
        "subcategory": "Malware",
    },
    {
        "subject": "Suspected malware on company laptop",
        "description": "I need help responding to a suspected malware infection on my work laptop.",
        "category": "SECURITY",
        "subcategory": "Malware",
    },

    # -------------------------------------------------
    # DATA REQUEST
    # -------------------------------------------------

    {
        "subject": "Request company data",
        "description": "I need to request access to a specific company data set.",
        "category": "SECURITY",
        "subcategory": "Data request",
    },
    {
        "subject": "Security data access request",
        "description": "Please help me submit a request for access to restricted company data.",
        "category": "SECURITY",
        "subcategory": "Data request",
    },
    {
        "subject": "Request access to sensitive data",
        "description": "I need authorized access to sensitive business data for my work.",
        "category": "SECURITY",
        "subcategory": "Data request",
    },
    {
        "subject": "Corporate data request",
        "description": "I need to submit a request for a company data set that is access controlled.",
        "category": "SECURITY",
        "subcategory": "Data request",
    },
    {
        "subject": "Request protected information",
        "description": "Please help me request access to protected company information.",
        "category": "SECURITY",
        "subcategory": "Data request",
    },
    {
        "subject": "Data access approval request",
        "description": "I need approval to access a restricted business data resource.",
        "category": "SECURITY",
        "subcategory": "Data request",
    },
    {
        "subject": "Request restricted company data",
        "description": "I need authorized access to a restricted data source for a business task.",
        "category": "SECURITY",
        "subcategory": "Data request",
    },
    {
        "subject": "Sensitive data access request",
        "description": "Please process my request to access sensitive corporate information.",
        "category": "SECURITY",
        "subcategory": "Data request",
    },
    {
        "subject": "Business information request",
        "description": "I need approved access to protected business information.",
        "category": "SECURITY",
        "subcategory": "Data request",
    },
    {
        "subject": "Request access to protected dataset",
        "description": "Please provide the process for requesting access to a protected company dataset.",
        "category": "SECURITY",
        "subcategory": "Data request",
    },
    {
        "subject": "Restricted data request",
        "description": "I need to request access to restricted information required for my work.",
        "category": "SECURITY",
        "subcategory": "Data request",
    },
    {
        "subject": "Request sensitive business information",
        "description": "I need authorized access to sensitive information for a business purpose.",
        "category": "SECURITY",
        "subcategory": "Data request",
    },
    {
        "subject": "Data permission request",
        "description": "Please help me request permission to access a restricted company dataset.",
        "category": "SECURITY",
        "subcategory": "Data request",
    },
    {
        "subject": "Corporate information access request",
        "description": "I need approved access to protected corporate information.",
        "category": "SECURITY",
        "subcategory": "Data request",
    },
    {
        "subject": "Request confidential data access",
        "description": "I need to submit a request to access confidential business data.",
        "category": "SECURITY",
        "subcategory": "Data request",
    },
    {
        "subject": "Protected data access needed",
        "description": "My work requires authorized access to a protected data source.",
        "category": "SECURITY",
        "subcategory": "Data request",
    },
    {
        "subject": "Request access to confidential information",
        "description": "Please process my request for access to confidential company information.",
        "category": "SECURITY",
        "subcategory": "Data request",
    },
    {
        "subject": "Secure data access request",
        "description": "I need authorized access to a restricted corporate data resource.",
        "category": "SECURITY",
        "subcategory": "Data request",
    },
]


def load_json(path):
    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def main():
    migrated = load_json(MIGRATED_PATH)
    resolved = load_json(RESOLVED_PATH)

    base_tickets = (
        migrated["tickets"]
        + resolved["tickets"]
    )

    if len(base_tickets) != 502:
        raise ValueError(
            "Expected 502 corrected base tickets."
        )

    print(
        "Corrected base tickets:",
        len(base_tickets),
    )

    print(
        "New SECURITY examples:",
        len(SECURITY_EXAMPLES),
    )

    if len(SECURITY_EXAMPLES) != 36:
        raise ValueError(
            "Expected exactly 36 SECURITY examples."
        )

    existing_keys = {
        (
            ticket["subject"].strip().lower(),
            ticket["description"].strip().lower(),
        )
        for ticket in base_tickets
    }

    duplicate_examples = [
        example
        for example in SECURITY_EXAMPLES
        if (
            example["subject"].strip().lower(),
            example["description"].strip().lower(),
        ) in existing_keys
    ]

    if duplicate_examples:
        raise ValueError(
            "Duplicate SECURITY examples found."
        )

    new_tickets = (
        base_tickets
        + SECURITY_EXAMPLES
    )

    output = {
        "taxonomy_version": "v2",
        "source_taxonomy_version": "v1",
        "taxonomy": [
            {
                "name": "SECURITY",
                "subcategories": [
                    "Phishing report",
                    "Malware",
                    "Suspicious activity",
                    "Data request",
                ],
            }
        ],
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

    print("\nSECURITY EXPANSION COMPLETE")
    print(
        "Total tickets:",
        len(new_tickets),
    )
    print(
        "SECURITY total:",
        sum(
            ticket["category"] == "SECURITY"
            for ticket in new_tickets
        ),
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