"""Helper functions."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

UTC = timezone.utc


def truebool(val: Any | None) -> bool:
    """Return `True` if the value passed in matches a "True" value, otherwise `False`.

    "True" values are: 'true', 't', 'yes', 'y', 'on' or '1'.
    """
    return val is not None and str(val).lower() in ("true", "t", "yes", "y", "on", "1")


def utc_timestamp_from_epoch(epoch: int | None) -> datetime | None:
    """Return the UTC timestamp from an epoch value."""
    return None if epoch is None else datetime.fromtimestamp(epoch, UTC)
