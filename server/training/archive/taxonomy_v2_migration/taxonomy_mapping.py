"""
Approved taxonomy migration plan.

This file is documentation + controlled mapping metadata.
It does NOT modify category_seed_data.json.
"""

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


# Safe one-to-one label renames where the existing examples
# preserve essentially the same meaning.
EXACT_RENAMES = {
    ("NETWORK", "DNS resolution"):
        ("NETWORK", "DNS"),

    ("VPN", "Certificate issue"):
        ("VPN", "Certificate"),

    ("ACCESS", "Account lockout"):
        ("ACCESS", "Account lockout"),

    ("ACCESS", "Permissions"):
        ("ACCESS", "Permissions"),

    ("APPLICATION", "Performance"):
        ("APPLICATION", "Performance"),

    ("EMAIL", "Mailbox"):
        ("EMAIL", "Mailbox"),

    ("EMAIL", "Calendar sync"):
        ("EMAIL", "Calendar"),

    ("HARDWARE", "Laptop"):
        ("HARDWARE", "Laptop"),

    ("HARDWARE", "Peripheral"):
        ("HARDWARE", "Peripheral"),

    ("SOFTWARE", "Licensing"):
        ("SOFTWARE", "Licensing"),

    ("SOFTWARE", "Installation"):
        ("SOFTWARE", "Installation"),

    ("SOFTWARE", "Update/patch"):
        ("SOFTWARE", "Update"),

    ("SOFTWARE", "Compatibility"):
        ("SOFTWARE", "Compatibility"),

    ("VPN", "Connection failure"):
        ("VPN", "Connection failure"),

    ("NETWORK", "Connectivity"):
        ("NETWORK", "Connectivity"),

    ("NETWORK", "Bandwidth"):
        ("NETWORK", "Bandwidth"),
}


# These labels cannot safely be converted by a blind rename.
# Their individual examples need semantic review or replacement.
MANUAL_REVIEW = {
    ("VPN", "Slow connection"),
    ("VPN", "Split tunneling"),

    ("ACCESS", "Role change"),
    ("ACCESS", "New access request"),

    ("APPLICATION", "Authentication"),
    ("APPLICATION", "Error/crash"),
    ("APPLICATION", "Feature request"),

    ("EMAIL", "Attachment issue"),
    ("EMAIL", "Spam/phishing"),

    ("HARDWARE", "Monitor"),
    ("HARDWARE", "Replacement"),

    ("NETWORK", "Firewall rules"),
}


# New approved categories that currently have zero examples.
NEW_CATEGORIES = {
    "PRINTER",
    "SECURITY",
    "UNCLASSIFIED",
}


# New approved subcategories that currently have no clean
# training examples.
NEW_SUBCATEGORIES = {
    "NETWORK": {
        "WiFi",
        "LAN",
    },
    "VPN": {
        "Client install",
        "Timeout",
    },
    "ACCESS": {
        "Password reset",
        "MFA",
        "Onboarding",
    },
    "SOFTWARE": {
        "Crash",
    },
    "HARDWARE": {
        "Desktop",
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
        "Distribution list",
        "Spam",
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
    },
}


def validate_mapping():
    """
    Validate the migration metadata before we use it.
    """

    for source, target in EXACT_RENAMES.items():

        source_category, source_subcategory = source
        target_category, target_subcategory = target

        if target_category not in APPROVED_TAXONOMY:
            raise ValueError(
                f"Invalid target category: {target_category}"
            )

        if (
            target_subcategory
            not in APPROVED_TAXONOMY[target_category]
        ):
            raise ValueError(
                f"Invalid target subcategory: "
                f"{target_category}/{target_subcategory}"
            )

        if source in MANUAL_REVIEW:
            raise ValueError(
                f"{source} cannot be both an exact rename "
                f"and manual review."
            )

    for category, subcategories in NEW_SUBCATEGORIES.items():

        if category not in APPROVED_TAXONOMY:
            raise ValueError(
                f"Unknown category in NEW_SUBCATEGORIES: "
                f"{category}"
            )

        for subcategory in subcategories:
            if (
                subcategory
                not in APPROVED_TAXONOMY[category]
            ):
                raise ValueError(
                    f"Unknown subcategory: "
                    f"{category}/{subcategory}"
                )

    print("TAXONOMY MAPPING VALID")
    print(
        "Exact renames:",
        len(EXACT_RENAMES)
    )
    print(
        "Manual review groups:",
        len(MANUAL_REVIEW)
    )
    print(
        "New categories:",
        len(NEW_CATEGORIES)
    )


if __name__ == "__main__":
    validate_mapping()