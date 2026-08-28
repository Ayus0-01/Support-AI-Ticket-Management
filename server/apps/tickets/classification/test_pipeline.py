from .pipeline import classify_ticket


tests = [
    (
        "Printer not printing",
        "My office printer accepts the print job but nothing comes out.",
        "TEAM",
        "YES",
        "HIGH",
        False,
    ),
    (
        "Suspicious email",
        "I received an email asking me to verify my company credentials through a suspicious link.",
        "JUST_ME",
        "NO",
        "HIGH",
        True,
    ),
    (
        "VPN certificate",
        "My corporate VPN certificate has expired and I cannot authenticate.",
        "JUST_ME",
        "YES",
        "HIGH",
        False,
    ),
    (
        "WiFi issue",
        "My laptop cannot connect to the office WiFi network.",
        "JUST_ME",
        "PARTIALLY",
        "MEDIUM",
        True,
    ),
    (
        "CRM performance",
        "The CRM application is extremely slow when loading customer records.",
        "TEAM",
        "PARTIALLY",
        "MEDIUM",
        True,
    ),
]


for (
    subject,
    description,
    scope,
    blocked,
    urgency,
    workaround,
) in tests:

    print("\n" + "=" * 80)
    print("TEST:", subject)
    print("=" * 80)

    result = classify_ticket(
        subject=subject,
        description=description,
        affected_scope=scope,
        work_blocked=blocked,
        urgent_feeling=urgency,
        workaround_available=workaround,
    )

    print(result)