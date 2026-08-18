SEVERITY_ORDER = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2,
    "CRITICAL": 3,
}


AFFECTED_SCOPE_ORDER = {
    "JUST_ME": 0,
    "TEAM": 1,
    "DEPARTMENT": 2,
    "ORGANISATION": 3,
}


def calculate_priority(
    severity,
    affected_scope,
):
    """
    Calculate ticket priority using the
    deterministic priority matrix.
    """

    # Critical incidents
    if severity == "CRITICAL":
        return "P1"

    # High severity
    if severity == "HIGH":

        if affected_scope in {
            "DEPARTMENT",
            "ORGANISATION",
        }:
            return "P1"

        if affected_scope == "TEAM":
            return "P2"

        return "P2"

    # Medium severity
    if severity == "MEDIUM":

        if affected_scope == "ORGANISATION":
            return "P2"

        if affected_scope == "DEPARTMENT":
            return "P2"

        if affected_scope == "TEAM":
            return "P3"

        return "P3"

    # Low severity
    if severity == "LOW":

        if affected_scope in {
            "DEPARTMENT",
            "ORGANISATION",
        }:
            return "P3"

        return "P4"

    # Safe fallback
    return "P4"

def explain_priority(
    severity,
    affected_scope,
    priority,
):
    """
    Explain why the deterministic priority matrix
    produced the final priority.
    """

    if severity == "CRITICAL":
        return (
            "Critical severity is assigned priority P1."
        )

    if severity == "HIGH":

        if affected_scope in {
            "DEPARTMENT",
            "ORGANISATION",
        }:
            return (
                "High severity affecting a department "
                "or the whole organisation is assigned P1."
            )

        if affected_scope == "TEAM":
            return (
                "High severity affecting a team "
                "is assigned P2."
            )

        return (
            "High severity affecting only the requester "
            "is assigned P2."
        )

    if severity == "MEDIUM":

        if affected_scope in {
            "DEPARTMENT",
            "ORGANISATION",
        }:
            return (
                "Medium severity affecting a department "
                "or the whole organisation is assigned P2."
            )

        if affected_scope == "TEAM":
            return (
                "Medium severity affecting a team "
                "is assigned P3."
            )

        return (
            "Medium severity affecting only the requester "
            "is assigned P3."
        )

    if severity == "LOW":

        if affected_scope in {
            "DEPARTMENT",
            "ORGANISATION",
        }:
            return (
                "Low severity affecting a department "
                "or the whole organisation is assigned P3."
            )

        if affected_scope == "TEAM":
            return (
                "Low severity affecting a team "
                "is assigned P3."
            )

        return (
            "Low severity affecting only the requester "
            "is assigned P4."
        )

    return (
        f"Priority {priority} was assigned by the "
        "deterministic priority matrix."
    )