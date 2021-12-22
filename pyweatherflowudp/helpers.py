"""Helper functions."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, TypeVar

from pint import Quantity
from pint.unit import Unit

DIRECTIONS = [
    "N",
    "NNE",
    "NE",
    "ENE",
    "E",
    "ESE",
    "SE",
    "SSE",
    "S",
    "SSW",
    "SW",
    "WSW",
    "W",
    "WNW",
    "NW",
    "NNW",
]
T = TypeVar("T")  # pylint: disable=invalid-name
UTC = timezone.utc


def degrees_to_cardinal(degree: float | Quantity[float]) -> str:
    """Convert degrees to a cardinal direction."""
    return DIRECTIONS[
        round(
            (degree.m if isinstance(degree, Quantity) else degree)
            / (360.0 / (directions_count := len(DIRECTIONS)))
        )
        % directions_count
    ]


def nvl(value: T | None, default: T) -> T:
    """Return default if value is None, else value."""
    return default if value is None else value


def truebool(val: Any | None) -> bool:
    """Return `True` if the value passed in matches a "True" value, otherwise `False`.

    "True" values are: 'true', 't', 'yes', 'y', 'on' or '1'.
    """
    return val is not None and str(val).lower() in ("true", "t", "yes", "y", "on", "1")


def utc_timestamp_from_epoch(epoch: int | None) -> datetime | None:
    """Return the UTC timestamp from an epoch value."""
    return None if epoch is None else datetime.fromtimestamp(epoch, UTC)


def value_as_unit(value: T | None, unit: Unit = None) -> T | Quantity[T] | None:
    """Return value as specified unit or sensor fault if value is none."""
    if value is None:
        return None
    if unit is None:
        return value
    return value * unit
