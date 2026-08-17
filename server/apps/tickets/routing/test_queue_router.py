from queue_router import determine_queue


def run_test(
    category,
    subcategory,
    severity,
    priority,
):
    queue = determine_queue(
        category=category,
        subcategory=subcategory,
        severity=severity,
        priority=priority,
    )

    print(
        f"{category:12} | "
        f"{subcategory:25} | "
        f"{severity:10} | "
        f"{priority:5} | "
        f"{queue}"
    )


print("=" * 100)
print("QUEUE ROUTING TEST")
print("=" * 100)

run_test(
    "VPN",
    "Connection failure",
    "HIGH",
    "P2",
)

run_test(
    "EMAIL",
    "Spam/phishing",
    "HIGH",
    "P2",
)

run_test(
    "HARDWARE",
    "Laptop",
    "MEDIUM",
    "P3",
)

run_test(
    "NETWORK",
    "DNS resolution",
    "HIGH",
    "P2",
)

run_test(
    "APPLICATION",
    "Error/crash",
    "HIGH",
    "P2",
)

run_test(
    "ACCESS",
    "Account lockout",
    "MEDIUM",
    "P3",
)

run_test(
    "SOFTWARE",
    "Installation",
    "LOW",
    "P4",
)

run_test(
    "EMAIL",
    "Mailbox",
    "LOW",
    "P4",
)

run_test(
    "VPN",
    "Certificate issue",
    "CRITICAL",
    "P1",
)

print("=" * 100)