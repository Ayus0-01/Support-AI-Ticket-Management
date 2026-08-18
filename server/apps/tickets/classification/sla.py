from datetime import datetime, timedelta, time

SLA_RULES = {
    "P1": {
        "first_response_minutes": 15,
        "resolution_hours": 4,
    },

    "P2": {
        "first_response_minutes": 60,
        "resolution_hours": 8,
    },

    "P3": {
        "first_response_minutes": 240,
        "resolution_hours": 24,
    },

    "P4": {
        "first_response_minutes": 480,
        "resolution_hours": 40,
    },
}

BUSINESS_START = time(9, 0)
BUSINESS_END = time(17, 0)

# Add company holidays here.
# Format: "YYYY-MM-DD"
HOLIDAYS = {
    # "2026-08-15",
    # "2026-08-26",
}

def is_business_day(date):
    """
    Return True if the date is a working day.
    """

    # Saturday = 5
    # Sunday = 6
    if date.weekday() >= 5:
        return False

    if date.isoformat() in HOLIDAYS:
        return False

    return True


def next_business_day(date):
    """
    Find the next working day.
    """

    current = date + timedelta(days=1)

    while not is_business_day(current):
        current += timedelta(days=1)

    return current


def move_to_business_time(dt):
    """
    Move a datetime into business hours.
    """

    if not is_business_day(dt.date()):
        next_day = dt.date()

        while not is_business_day(next_day):
            next_day += timedelta(days=1)

        return datetime.combine(
            next_day,
            BUSINESS_START
        )

    if dt.time() < BUSINESS_START:
        return datetime.combine(
            dt.date(),
            BUSINESS_START
        )

    if dt.time() >= BUSINESS_END:
        next_day = next_business_day(dt.date())

        return datetime.combine(
            next_day,
            BUSINESS_START
        )

    return dt


def add_business_minutes(start_datetime, minutes):
    """
    Add business minutes while skipping weekends,
    holidays and non-working hours.
    """

    current = move_to_business_time(
        start_datetime
    )

    remaining = minutes

    while remaining > 0:

        current = move_to_business_time(current)

        business_end = datetime.combine(
            current.date(),
            BUSINESS_END
        )

        available_today = int(
            (business_end - current).total_seconds()
            / 60
        )

        if remaining <= available_today:

            return current + timedelta(
                minutes=remaining
            )

        remaining -= available_today

        current = datetime.combine(
            next_business_day(current.date()),
            BUSINESS_START
        )

    return current


def add_business_hours(start_datetime, hours):
    """
    Add business hours.
    """

    return add_business_minutes(
        start_datetime,
        int(hours * 60)
    )

def calculate_sla(priority, created_at=None):
    """
    Calculate first-response and resolution deadlines.
    """

    if priority not in SLA_RULES:
        raise ValueError(
            f"Unknown priority: {priority}"
        )

    if created_at is None:
        created_at = datetime.now()

    created_at = move_to_business_time(
        created_at
    )

    rules = SLA_RULES[priority]

    first_response_due = add_business_minutes(
        created_at,
        rules["first_response_minutes"]
    )

    resolution_due = add_business_hours(
        created_at,
        rules["resolution_hours"]
    )

    return {
        "priority": priority,
        "first_response_due": first_response_due,
        "resolution_due": resolution_due,
    }