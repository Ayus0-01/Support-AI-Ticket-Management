import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

INPUT_PATH = (
    BASE_DIR / "category_seed_data_v2_deduped.json"
)

OUTPUT_PATH = (
    BASE_DIR / "category_seed_data_v2_curated.json"
)


KEEP_SUBJECTS = {
    # VPN / slow connection
    "VPN is very slow",
    "VPN performance issue",
    "VPN connection is slow",

    # VPN / split tunneling
    "Need split tunneling",
    "Split tunneling not working",
    "VPN selective routing",

    # NETWORK / firewall rules
    "Firewall blocking application",
    "Need firewall rule",
    "Open firewall port",

    # APPLICATION / authentication
    "Application login failing",
    "Application credentials rejected",
    "Cannot log into application",

    # APPLICATION / feature request
    "Request new application feature",
    "Feature improvement needed",
    "New application capability",

    # ACCESS / role change
    "Change user role",
    "Department role update",
    "Employee role update",

    # ACCESS / new access request
    "Request new system access",
    "Access request",
    "New user access",

    # EMAIL / attachment issue
    "Cannot send attachment",
    "Large attachment issue",
    "Unable to open email attachment",

    # HARDWARE / replacement
    "Hardware replacement needed",
    "Request new company device",
    "Company device replacement",
}


def main():
    with open(
        INPUT_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    tickets = data["tickets"]

    unclassified = [
        ticket
        for ticket in tickets
        if ticket["category"] == "UNCLASSIFIED"
    ]

    kept_subjects = {
        ticket["subject"]
        for ticket in unclassified
        if ticket["subject"] in KEEP_SUBJECTS
    }

    missing = KEEP_SUBJECTS - kept_subjects

    if missing:
        raise ValueError(
            "Could not find expected UNCLASSIFIED "
            f"examples: {sorted(missing)}"
        )

    kept_unclassified = [
        ticket
        for ticket in unclassified
        if ticket["subject"] in KEEP_SUBJECTS
    ]

    if len(kept_unclassified) != 30:
        raise ValueError(
            f"Expected 30 UNCLASSIFIED examples, "
            f"got {len(kept_unclassified)}"
        )

    retained = [
        ticket
        for ticket in tickets
        if ticket["category"] != "UNCLASSIFIED"
    ]

    final_tickets = (
        retained + kept_unclassified
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
    print("UNCLASSIFIED CURATION COMPLETE")
    print("=" * 90)
    print(
        "Original tickets:",
        len(tickets),
    )
    print(
        "Original UNCLASSIFIED:",
        len(unclassified),
    )
    print(
        "Retained UNCLASSIFIED:",
        len(kept_unclassified),
    )
    print(
        "Final tickets:",
        len(final_tickets),
    )
    print(
        "Output:",
        OUTPUT_PATH,
    )


if __name__ == "__main__":
    main()