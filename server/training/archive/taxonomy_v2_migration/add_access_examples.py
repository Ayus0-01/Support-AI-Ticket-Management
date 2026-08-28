import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

SOURCE_PATH = (
    BASE_DIR / "category_seed_data_migrated.json"
)

OUTPUT_PATH = (
    BASE_DIR / "category_seed_data_access_expanded.json"
)


ACCESS_EXAMPLES = [
    # -------------------------------------------------
    # PASSWORD RESET
    # -------------------------------------------------

    {
        "subject": "Forgot my account password",
        "description": "I forgot my company account password and need to reset it.",
        "category": "ACCESS",
        "subcategory": "Password reset",
    },
    {
        "subject": "Need password reset",
        "description": "I cannot remember my corporate password and need help resetting it.",
        "category": "ACCESS",
        "subcategory": "Password reset",
    },
    {
        "subject": "Reset corporate password",
        "description": "Please help me reset the password for my work account.",
        "category": "ACCESS",
        "subcategory": "Password reset",
    },
    {
        "subject": "Password forgotten",
        "description": "I have forgotten my login password and need to create a new one.",
        "category": "ACCESS",
        "subcategory": "Password reset",
    },
    {
        "subject": "Unable to remember password",
        "description": "I cannot remember my company account password and need a reset.",
        "category": "ACCESS",
        "subcategory": "Password reset",
    },
    {
        "subject": "Change forgotten account password",
        "description": "My work account password is forgotten and needs to be reset.",
        "category": "ACCESS",
        "subcategory": "Password reset",
    },
    {
        "subject": "Password reset assistance",
        "description": "I need assistance resetting my corporate account password.",
        "category": "ACCESS",
        "subcategory": "Password reset",
    },
    {
        "subject": "Reset my login password",
        "description": "Please reset the login password for my company account.",
        "category": "ACCESS",
        "subcategory": "Password reset",
    },
    {
        "subject": "Cannot access account after forgetting password",
        "description": "I cannot sign in because I forgot my account password.",
        "category": "ACCESS",
        "subcategory": "Password reset",
    },
    {
        "subject": "Corporate password reset request",
        "description": "I need a password reset for my corporate user account.",
        "category": "ACCESS",
        "subcategory": "Password reset",
    },
    {
        "subject": "Work account password forgotten",
        "description": "I forgot the password used for my work account and need a reset.",
        "category": "ACCESS",
        "subcategory": "Password reset",
    },
    {
        "subject": "Help resetting account password",
        "description": "Please help me reset the password associated with my company account.",
        "category": "ACCESS",
        "subcategory": "Password reset",
    },
    {
        "subject": "Lost password",
        "description": "I no longer remember my corporate login password.",
        "category": "ACCESS",
        "subcategory": "Password reset",
    },
    {
        "subject": "Password recovery request",
        "description": "I need to recover access by resetting my forgotten work password.",
        "category": "ACCESS",
        "subcategory": "Password reset",
    },
    {
        "subject": "Account password needs reset",
        "description": "My company account password needs to be reset because I forgot it.",
        "category": "ACCESS",
        "subcategory": "Password reset",
    },
    {
        "subject": "Reset forgotten work password",
        "description": "Please assist with resetting the forgotten password for my work account.",
        "category": "ACCESS",
        "subcategory": "Password reset",
    },
    {
        "subject": "Forgotten corporate login credentials",
        "description": "I forgot my login password and need assistance recovering access.",
        "category": "ACCESS",
        "subcategory": "Password reset",
    },
    {
        "subject": "Password recovery for work account",
        "description": "I need to reset the password on my company account.",
        "category": "ACCESS",
        "subcategory": "Password reset",
    },

    # -------------------------------------------------
    # MFA
    # -------------------------------------------------

    {
        "subject": "MFA code not received",
        "description": "I am not receiving the verification code required for MFA login.",
        "category": "ACCESS",
        "subcategory": "MFA",
    },
    {
        "subject": "Multi-factor authentication failing",
        "description": "My MFA verification is failing when I try to sign in.",
        "category": "ACCESS",
        "subcategory": "MFA",
    },
    {
        "subject": "Authenticator app problem",
        "description": "The authenticator app is not generating a valid verification code.",
        "category": "ACCESS",
        "subcategory": "MFA",
    },
    {
        "subject": "MFA verification issue",
        "description": "I cannot complete the multi-factor authentication step during login.",
        "category": "ACCESS",
        "subcategory": "MFA",
    },
    {
        "subject": "MFA device changed",
        "description": "I changed my phone and need my new device configured for MFA.",
        "category": "ACCESS",
        "subcategory": "MFA",
    },
    {
        "subject": "Cannot complete MFA login",
        "description": "My account login stops because MFA verification cannot be completed.",
        "category": "ACCESS",
        "subcategory": "MFA",
    },
    {
        "subject": "Authenticator code rejected",
        "description": "The MFA code generated by my authenticator is being rejected.",
        "category": "ACCESS",
        "subcategory": "MFA",
    },
    {
        "subject": "MFA prompt not working",
        "description": "The multi-factor authentication prompt is not completing successfully.",
        "category": "ACCESS",
        "subcategory": "MFA",
    },
    {
        "subject": "Verification code problem",
        "description": "The verification code for my work account MFA is not working.",
        "category": "ACCESS",
        "subcategory": "MFA",
    },
    {
        "subject": "MFA enrollment issue",
        "description": "I am unable to enroll my account in multi-factor authentication.",
        "category": "ACCESS",
        "subcategory": "MFA",
    },
    {
        "subject": "New phone MFA setup",
        "description": "I need to register my new phone as the MFA device for my work account.",
        "category": "ACCESS",
        "subcategory": "MFA",
    },
    {
        "subject": "MFA authentication failure",
        "description": "The MFA authentication step fails every time I sign in.",
        "category": "ACCESS",
        "subcategory": "MFA",
    },
    {
        "subject": "Authenticator not approving login",
        "description": "The authenticator approval is not allowing me to complete login.",
        "category": "ACCESS",
        "subcategory": "MFA",
    },
    {
        "subject": "MFA reset request",
        "description": "I need my multi-factor authentication configuration reset.",
        "category": "ACCESS",
        "subcategory": "MFA",
    },
    {
        "subject": "Unable to verify MFA",
        "description": "I cannot verify my identity using the configured MFA method.",
        "category": "ACCESS",
        "subcategory": "MFA",
    },
    {
        "subject": "MFA token invalid",
        "description": "The MFA token provided during login is being reported as invalid.",
        "category": "ACCESS",
        "subcategory": "MFA",
    },
    {
        "subject": "MFA challenge failing",
        "description": "The authentication challenge fails when I attempt to access my work account.",
        "category": "ACCESS",
        "subcategory": "MFA",
    },
    {
        "subject": "Multi-factor login issue",
        "description": "I am unable to complete the MFA portion of my corporate login.",
        "category": "ACCESS",
        "subcategory": "MFA",
    },

    # -------------------------------------------------
    # ONBOARDING
    # -------------------------------------------------

    {
        "subject": "New employee access setup",
        "description": "A new employee has joined the team and needs initial system access.",
        "category": "ACCESS",
        "subcategory": "Onboarding",
    },
    {
        "subject": "New starter account setup",
        "description": "Please arrange the required accounts and access for a new starter.",
        "category": "ACCESS",
        "subcategory": "Onboarding",
    },
    {
        "subject": "Onboarding access request",
        "description": "A newly joined employee needs the standard systems required for onboarding.",
        "category": "ACCESS",
        "subcategory": "Onboarding",
    },
    {
        "subject": "New hire system access",
        "description": "Our new hire needs initial access to the systems required for their role.",
        "category": "ACCESS",
        "subcategory": "Onboarding",
    },
    {
        "subject": "Set up access for new employee",
        "description": "Please provision the standard work accounts for a new employee joining the team.",
        "category": "ACCESS",
        "subcategory": "Onboarding",
    },
    {
        "subject": "Employee onboarding accounts",
        "description": "A new employee requires the necessary accounts and permissions for their first day.",
        "category": "ACCESS",
        "subcategory": "Onboarding",
    },
    {
        "subject": "New starter access provisioning",
        "description": "Please provision access for a new starter joining our department.",
        "category": "ACCESS",
        "subcategory": "Onboarding",
    },
    {
        "subject": "First day access setup",
        "description": "A new employee needs their standard company systems configured before their first day.",
        "category": "ACCESS",
        "subcategory": "Onboarding",
    },
    {
        "subject": "New joiner account provisioning",
        "description": "Please create and provision the required work access for a new joiner.",
        "category": "ACCESS",
        "subcategory": "Onboarding",
    },
    {
        "subject": "New employee system provisioning",
        "description": "Our new employee needs the standard accounts and system access for their role.",
        "category": "ACCESS",
        "subcategory": "Onboarding",
    },
    {
        "subject": "Employee onboarding support",
        "description": "Please arrange initial system access for an employee starting with the company.",
        "category": "ACCESS",
        "subcategory": "Onboarding",
    },
    {
        "subject": "New hire account creation",
        "description": "A new hire needs the standard corporate accounts created for their first day.",
        "category": "ACCESS",
        "subcategory": "Onboarding",
    },
    {
        "subject": "Onboarding permissions setup",
        "description": "Please configure the standard permissions required by a newly hired employee.",
        "category": "ACCESS",
        "subcategory": "Onboarding",
    },
    {
        "subject": "New employee access provisioning",
        "description": "Our new employee needs initial access to the approved systems for their position.",
        "category": "ACCESS",
        "subcategory": "Onboarding",
    },
    {
        "subject": "New starter login setup",
        "description": "Please prepare the corporate account and required access for a new starter.",
        "category": "ACCESS",
        "subcategory": "Onboarding",
    },
    {
        "subject": "New hire IT access",
        "description": "A new team member requires the standard IT access needed for their job.",
        "category": "ACCESS",
        "subcategory": "Onboarding",
    },
    {
        "subject": "Employee joining next week",
        "description": "Please prepare the required accounts and systems for an employee joining next week.",
        "category": "ACCESS",
        "subcategory": "Onboarding",
    },
    {
        "subject": "Initial access for new employee",
        "description": "A new employee needs initial corporate system access as part of onboarding.",
        "category": "ACCESS",
        "subcategory": "Onboarding",
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

    print("Existing tickets:", len(existing))
    print("New ACCESS examples:", len(ACCESS_EXAMPLES))

    if len(ACCESS_EXAMPLES) != 54:
        raise ValueError(
            "Expected exactly 54 ACCESS examples."
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
        for example in ACCESS_EXAMPLES
        if (
            example["subject"].strip().lower(),
            example["description"].strip().lower(),
        )
        in existing_keys
    ]

    if duplicate_examples:
        raise ValueError(
            "Duplicate ACCESS examples found."
        )

    new_tickets = (
        existing + ACCESS_EXAMPLES
    )

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

    print("\nACCESS EXPANSION COMPLETE")
    print(
        "Total tickets:",
        len(new_tickets),
    )
    print(
        "ACCESS total:",
        sum(
            ticket["category"] == "ACCESS"
            for ticket in new_tickets
        ),
    )
    print(
        "Output:",
        OUTPUT_PATH,
    )
    print(
        "\nOriginal migrated dataset was NOT modified."
    )


if __name__ == "__main__":
    main()