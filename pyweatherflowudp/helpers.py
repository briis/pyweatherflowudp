"""Helper functions."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, TypeVar, cast

from pint import Quantity, Unit

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
DIRECTIONS_COUNT = len(DIRECTIONS)
T = TypeVar("T")  # pylint: disable=invalid-name
UTC = timezone.utc


def degrees_to_cardinal(degree: float | Quantity[float]) -> str:
    """Convert degrees to a cardinal direction."""
    _deg = cast(float, degree.m if isinstance(degree, Quantity) else degree)
    return DIRECTIONS[round(_deg / (360.0 / DIRECTIONS_COUNT)) % DIRECTIONS_COUNT]


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
