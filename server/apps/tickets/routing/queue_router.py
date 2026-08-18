def determine_queue(
    category,
    subcategory,
    severity,
    priority,
):
    """
    Determine the support queue for a classified ticket.

    Priority is the main routing factor.
    Category/subcategory provide additional routing
    for specialised support queues.
    """

    category = (category or "").upper()
    subcategory = (subcategory or "").lower()
    severity = (severity or "").upper()
    priority = (priority or "").upper()

    if priority == "P1":
        return "CRITICAL_QUEUE"

    if category == "EMAIL" and "phishing" in subcategory:
        return "SECURITY_QUEUE"

    if category == "SECURITY":
        return "SECURITY_QUEUE"

    if category == "HARDWARE":
        return "HARDWARE_QUEUE"

    if category in {"NETWORK", "VPN"}:
        return "NETWORK_QUEUE"

    if category in {"APPLICATION", "SOFTWARE"}:
        return "APPLICATION_QUEUE"

    if category == "ACCESS":
        return "ACCESS_QUEUE"

    if category == "EMAIL":
        return "EMAIL_QUEUE"

    if severity == "CRITICAL":
        return "CRITICAL_QUEUE"

    if severity == "HIGH":
        return "HIGH_PRIORITY_QUEUE"

    if priority == "P2":
        return "HIGH_PRIORITY_QUEUE"

    if priority == "P3":
        return "STANDARD_QUEUE"

    if priority == "P4":
        return "LOW_PRIORITY_QUEUE"

    return "GENERAL_QUEUE"