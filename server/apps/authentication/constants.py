USER_ROLES = ("User", "Agent", "Support Manager", "Admin")


def normalize_user_role(role):
    """Map the retired Manager role onto the sole supported manager role."""
    return "Support Manager" if role == "Manager" else role
