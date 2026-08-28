import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

SOURCE_PATH = (
    BASE_DIR
    / "datasets"
    / "severity_seed_data.json"
)

OUTPUT_PATH = (
    BASE_DIR
    / "datasets"
    / "severity_seed_data_v2.json"
)


NEW_SEVERITY_EXAMPLES = [
    # =================================================
    # PRINTER
    # =================================================

    {
        "affected_scope": "JUST_ME",
        "work_blocked": "NO",
        "urgent_feeling": "LOW",
        "workaround_available": True,
        "category": "PRINTER",
        "severity": "LOW",
    },
    {
        "affected_scope": "JUST_ME",
        "work_blocked": "NO",
        "urgent_feeling": "LOW",
        "workaround_available": True,
        "category": "PRINTER",
        "severity": "LOW",
    },
    {
        "affected_scope": "TEAM",
        "work_blocked": "NO",
        "urgent_feeling": "LOW",
        "workaround_available": True,
        "category": "PRINTER",
        "severity": "LOW",
    },
    {
        "affected_scope": "TEAM",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "LOW",
        "workaround_available": True,
        "category": "PRINTER",
        "severity": "LOW",
    },

    {
        "affected_scope": "JUST_ME",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "MEDIUM",
        "workaround_available": True,
        "category": "PRINTER",
        "severity": "MEDIUM",
    },
    {
        "affected_scope": "TEAM",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "MEDIUM",
        "workaround_available": True,
        "category": "PRINTER",
        "severity": "MEDIUM",
    },
    {
        "affected_scope": "TEAM",
        "work_blocked": "YES",
        "urgent_feeling": "MEDIUM",
        "workaround_available": True,
        "category": "PRINTER",
        "severity": "MEDIUM",
    },
    {
        "affected_scope": "DEPARTMENT",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "MEDIUM",
        "workaround_available": False,
        "category": "PRINTER",
        "severity": "MEDIUM",
    },
    {
        "affected_scope": "DEPARTMENT",
        "work_blocked": "YES",
        "urgent_feeling": "MEDIUM",
        "workaround_available": True,
        "category": "PRINTER",
        "severity": "MEDIUM",
    },

    {
        "affected_scope": "TEAM",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "PRINTER",
        "severity": "HIGH",
    },
    {
        "affected_scope": "DEPARTMENT",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": True,
        "category": "PRINTER",
        "severity": "HIGH",
    },
    {
        "affected_scope": "DEPARTMENT",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "PRINTER",
        "severity": "HIGH",
    },
    {
        "affected_scope": "ORGANISATION",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "PRINTER",
        "severity": "HIGH",
    },
    {
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": True,
        "category": "PRINTER",
        "severity": "HIGH",
    },

    {
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "PRINTER",
        "severity": "CRITICAL",
    },
    {
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "PRINTER",
        "severity": "CRITICAL",
    },
    {
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "PRINTER",
        "severity": "CRITICAL",
    },
    {
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "MEDIUM",
        "workaround_available": False,
        "category": "PRINTER",
        "severity": "CRITICAL",
    },

    # =================================================
    # SECURITY
    # =================================================

    {
        "affected_scope": "JUST_ME",
        "work_blocked": "NO",
        "urgent_feeling": "LOW",
        "workaround_available": True,
        "category": "SECURITY",
        "severity": "LOW",
    },
    {
        "affected_scope": "JUST_ME",
        "work_blocked": "NO",
        "urgent_feeling": "LOW",
        "workaround_available": True,
        "category": "SECURITY",
        "severity": "LOW",
    },
    {
        "affected_scope": "TEAM",
        "work_blocked": "NO",
        "urgent_feeling": "LOW",
        "workaround_available": True,
        "category": "SECURITY",
        "severity": "LOW",
    },
    {
        "affected_scope": "TEAM",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "LOW",
        "workaround_available": True,
        "category": "SECURITY",
        "severity": "LOW",
    },

    {
        "affected_scope": "JUST_ME",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "MEDIUM",
        "workaround_available": True,
        "category": "SECURITY",
        "severity": "MEDIUM",
    },
    {
        "affected_scope": "TEAM",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "MEDIUM",
        "workaround_available": True,
        "category": "SECURITY",
        "severity": "MEDIUM",
    },
    {
        "affected_scope": "TEAM",
        "work_blocked": "YES",
        "urgent_feeling": "MEDIUM",
        "workaround_available": True,
        "category": "SECURITY",
        "severity": "MEDIUM",
    },
    {
        "affected_scope": "DEPARTMENT",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "MEDIUM",
        "workaround_available": False,
        "category": "SECURITY",
        "severity": "MEDIUM",
    },
    {
        "affected_scope": "DEPARTMENT",
        "work_blocked": "YES",
        "urgent_feeling": "MEDIUM",
        "workaround_available": True,
        "category": "SECURITY",
        "severity": "MEDIUM",
    },

    {
        "affected_scope": "TEAM",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "SECURITY",
        "severity": "HIGH",
    },
    {
        "affected_scope": "DEPARTMENT",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": True,
        "category": "SECURITY",
        "severity": "HIGH",
    },
    {
        "affected_scope": "DEPARTMENT",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "SECURITY",
        "severity": "HIGH",
    },
    {
        "affected_scope": "ORGANISATION",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "SECURITY",
        "severity": "HIGH",
    },
    {
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": True,
        "category": "SECURITY",
        "severity": "HIGH",
    },

    {
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "SECURITY",
        "severity": "CRITICAL",
    },
    {
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "SECURITY",
        "severity": "CRITICAL",
    },
    {
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "SECURITY",
        "severity": "CRITICAL",
    },
    {
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "MEDIUM",
        "workaround_available": False,
        "category": "SECURITY",
        "severity": "CRITICAL",
    },

    # =================================================
    # UNCLASSIFIED
    # =================================================

    {
        "affected_scope": "JUST_ME",
        "work_blocked": "NO",
        "urgent_feeling": "LOW",
        "workaround_available": True,
        "category": "UNCLASSIFIED",
        "severity": "LOW",
    },
    {
        "affected_scope": "JUST_ME",
        "work_blocked": "NO",
        "urgent_feeling": "LOW",
        "workaround_available": True,
        "category": "UNCLASSIFIED",
        "severity": "LOW",
    },
    {
        "affected_scope": "TEAM",
        "work_blocked": "NO",
        "urgent_feeling": "LOW",
        "workaround_available": True,
        "category": "UNCLASSIFIED",
        "severity": "LOW",
    },
    {
        "affected_scope": "TEAM",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "LOW",
        "workaround_available": True,
        "category": "UNCLASSIFIED",
        "severity": "LOW",
    },

    {
        "affected_scope": "JUST_ME",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "MEDIUM",
        "workaround_available": True,
        "category": "UNCLASSIFIED",
        "severity": "MEDIUM",
    },
    {
        "affected_scope": "TEAM",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "MEDIUM",
        "workaround_available": True,
        "category": "UNCLASSIFIED",
        "severity": "MEDIUM",
    },
    {
        "affected_scope": "TEAM",
        "work_blocked": "YES",
        "urgent_feeling": "MEDIUM",
        "workaround_available": True,
        "category": "UNCLASSIFIED",
        "severity": "MEDIUM",
    },
    {
        "affected_scope": "DEPARTMENT",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "MEDIUM",
        "workaround_available": False,
        "category": "UNCLASSIFIED",
        "severity": "MEDIUM",
    },
    {
        "affected_scope": "DEPARTMENT",
        "work_blocked": "YES",
        "urgent_feeling": "MEDIUM",
        "workaround_available": True,
        "category": "UNCLASSIFIED",
        "severity": "MEDIUM",
    },

    {
        "affected_scope": "TEAM",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "UNCLASSIFIED",
        "severity": "HIGH",
    },
    {
        "affected_scope": "DEPARTMENT",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": True,
        "category": "UNCLASSIFIED",
        "severity": "HIGH",
    },
    {
        "affected_scope": "DEPARTMENT",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "UNCLASSIFIED",
        "severity": "HIGH",
    },
    {
        "affected_scope": "ORGANISATION",
        "work_blocked": "PARTIALLY",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "UNCLASSIFIED",
        "severity": "HIGH",
    },
    {
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": True,
        "category": "UNCLASSIFIED",
        "severity": "HIGH",
    },

    {
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "UNCLASSIFIED",
        "severity": "CRITICAL",
    },
    {
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "UNCLASSIFIED",
        "severity": "CRITICAL",
    },
    {
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "HIGH",
        "workaround_available": False,
        "category": "UNCLASSIFIED",
        "severity": "CRITICAL",
    },
    {
        "affected_scope": "ORGANISATION",
        "work_blocked": "YES",
        "urgent_feeling": "MEDIUM",
        "workaround_available": False,
        "category": "UNCLASSIFIED",
        "severity": "CRITICAL",
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

    corrected_existing = []
    software_conflict_seen = False

    for ticket in existing:
        if (
            ticket.get("affected_scope") == "DEPARTMENT"
            and ticket.get("work_blocked") == "PARTIALLY"
            and ticket.get("urgent_feeling") == "LOW"
            and ticket.get("workaround_available") is True
            and ticket.get("category") == "SOFTWARE"
            and ticket.get("severity") == "HIGH"
            and not software_conflict_seen
        ):
            corrected_ticket = dict(ticket)
            corrected_ticket["severity"] = "MEDIUM"
            corrected_existing.append(corrected_ticket)
            software_conflict_seen = True
        else:
            corrected_existing.append(ticket)

    if not software_conflict_seen:
        raise ValueError(
            "Expected the pre-existing SOFTWARE severity conflict "
            "to be present in the original dataset."
        )

    print(
        "Existing severity tickets:",
        len(existing),
    )

    print(
        "New severity tickets:",
        len(NEW_SEVERITY_EXAMPLES),
    )

    if len(NEW_SEVERITY_EXAMPLES) != 54:
        raise ValueError(
            "Expected exactly 54 new severity examples."
        )

    existing_categories = {
        ticket.get("category")
        for ticket in existing
    }

    missing_categories = {
        "PRINTER",
        "SECURITY",
        "UNCLASSIFIED",
    } - existing_categories

    if missing_categories != {
        "PRINTER",
        "SECURITY",
        "UNCLASSIFIED",
    }:
        raise ValueError(
            "Expected all three new categories "
            "to be absent from the old dataset."
        )

    new_data = {
        "tickets": (
            corrected_existing
            + NEW_SEVERITY_EXAMPLES
        )
    }

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            new_data,
            file,
            indent=2,
        )

    print(
        "\nSEVERITY DATASET V2 CREATED"
    )

    print(
        "Final tickets:",
        len(
            new_data["tickets"]
        ),
    )

    print(
        "Output:",
        OUTPUT_PATH,
    )

    print(
        "\nOriginal severity dataset was NOT modified."
    )


if __name__ == "__main__":
    main()