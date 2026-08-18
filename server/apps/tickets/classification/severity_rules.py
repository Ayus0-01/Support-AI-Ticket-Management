SEVERITY_ORDER = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2,
    "CRITICAL": 3,
}


def raise_severity(
    current_severity,
    minimum_severity,
):
    """
    Raise severity when the deterministic rule
    requires a higher minimum severity.
    """

    if (
        SEVERITY_ORDER[minimum_severity]
        > SEVERITY_ORDER[current_severity]
    ):
        return minimum_severity

    return current_severity


def apply_severity_overrides(
    severity,
    category,
    affected_scope,
    is_vip=False,
    subject="",
    description="",
    similar_tickets_last_hour=0,
):
    """
    Apply deterministic severity override rules.

    Rules can only increase severity.
    """

    final_severity = severity

    rules_fired = []

    text = (
        f"{subject or ''} "
        f"{description or ''}"
    ).lower()

    # VIP users are at least HIGH.
    if is_vip:
        new_severity = raise_severity(
            final_severity,
            "HIGH"
        )

        if new_severity != final_severity:
            rules_fired.append(
                "VIP user requires minimum HIGH severity"
            )

        final_severity = new_severity

    # Organisation-wide impact is at least HIGH.
    if affected_scope == "ORGANISATION":
        new_severity = raise_severity(
            final_severity,
            "HIGH"
        )

        if new_severity != final_severity:
            rules_fired.append(
                "Organisation-wide impact requires minimum HIGH severity"
            )

        final_severity = new_severity

    # Site outage is at least HIGH.
    if "site down" in text:
        new_severity = raise_severity(
            final_severity,
            "HIGH"
        )

        if new_severity != final_severity:
            rules_fired.append(
                "Site outage requires minimum HIGH severity"
            )

        final_severity = new_severity

    # Security category is at least HIGH.
    if category == "SECURITY":
        new_severity = raise_severity(
            final_severity,
            "HIGH"
        )

        if new_severity != final_severity:
            rules_fired.append(
                "Security category requires minimum HIGH severity"
            )

        final_severity = new_severity

    # Emerging incident signal.
    if similar_tickets_last_hour >= 5:
        new_severity = raise_severity(
            final_severity,
            "HIGH"
        )

        if new_severity != final_severity:
            rules_fired.append(
                "Five or more similar tickets in one hour"
            )

        final_severity = new_severity

    return {
        "severity": final_severity,
        "rules_fired": rules_fired,
    }