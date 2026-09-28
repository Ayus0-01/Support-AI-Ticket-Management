from datetime import timezone as datetime_timezone

from rest_framework import serializers


class UTCDateTimeField(serializers.DateTimeField):
    """Serialize MongoDB timestamps as UTC even when they are naive datetimes."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("default_timezone", datetime_timezone.utc)
        super().__init__(*args, **kwargs)
