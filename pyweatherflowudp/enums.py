"""Enums module."""
from __future__ import annotations

from enum import IntEnum, unique


@unique
class PowerSaveMode(IntEnum):
    """Power save modes."""

    MODE_0 = 0
    MODE_1 = 1
    MODE_2 = 2
    MODE_3 = 3

    # Handle unknown/future power save modes
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, _: object) -> PowerSaveMode:  # pragma: no cover
        """Return default if not found."""
        return cls.UNKNOWN


@unique
class PrecipitationType(IntEnum):
    """Precipitation types."""

    NONE = 0
    RAIN = 1
    HAIL = 2
    RAIN_HAIL = 3

    # Handle unknown/future precipitation types
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, _: object) -> PrecipitationType:  # pragma: no cover
        """Return default if not found."""
        return cls.UNKNOWN


@unique
class RadioStatus(IntEnum):
    """Radio statuses."""

    RADIO_OFF = 0
    RADIO_ON = 1
    RADIO_ACTIVE = 3
    BLE_CONNECTED = 7

    # Handle unknown/future radio statuses
    UNKNOWN = -1

    @classmethod
    def _missing_(cls, _: object) -> RadioStatus:  # pragma: no cover
        """Return a default if not found."""
        return cls.UNKNOWN
