CATEGORY_TO_TEAM = {
    "VPN": "NETWORK_SUPPORT",
    "NETWORK": "NETWORK_SUPPORT",
    "HARDWARE": "HARDWARE_SUPPORT",
    "SOFTWARE": "APPLICATION_SUPPORT",
    "APPLICATION": "APPLICATION_SUPPORT",
    "ACCESS": "ACCESS_MANAGEMENT",
    "EMAIL": "EMAIL_SUPPORT",
    "SECURITY": "SECURITY_OPERATIONS",
    "UNCLASSIFIED": "GENERAL_SUPPORT",
}


def route_ticket(category):
    """
    Route a classified ticket to its default team queue.

    The routing decision is deterministic.
    Category -> default team.
    """

    category = (category or "UNCLASSIFIED").upper()

    team = CATEGORY_TO_TEAM.get(
        category,
        "GENERAL_SUPPORT"
    )

    return team