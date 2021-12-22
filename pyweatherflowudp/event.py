"""Events for WeatherFlow devices."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from pint import Quantity

from .const import UNIT_DEGREES, UNIT_KILOMETERS, UNIT_METERS_PER_SECOND
from .helpers import nvl, utc_timestamp_from_epoch

# pylint: disable=line-too-long


@dataclass
class Event:
    """Event base class."""

    _epoch: int

    @property
    def epoch(self) -> int:
        """Return epoch in seconds."""
        return self._epoch

    @property
    def timestamp(self) -> datetime | None:
        """Return the timestamp in UTC."""
        return utc_timestamp_from_epoch(self._epoch)

    def __repr__(self) -> str:  # pragma: no cover
        """Return repr(self)."""
        return f"Event<timestamp={self.timestamp}>"


@dataclass
class LightningStrikeEvent(Event):
    """Lightning strike event class."""

    _distance: float | None
    _energy: int | None

    @property
    def distance(self) -> Quantity[float]:
        """Return the distance in kilometers."""
        return nvl(self._distance, 0) * UNIT_KILOMETERS

    @property
    def energy(self) -> int:
        """Return the energy.

        Energy is just a pure number and has no physical meaning.
        """
        return nvl(self._energy, 0)

    def __repr__(self) -> str:  # pragma: no cover
        """Return repr(self)."""
        return (
            f"Lightning Strike Event<timestamp={self.timestamp}, speed={self.distance}>"
        )


@dataclass
class RainStartEvent(Event):
    """Rain start event class."""

    def __repr__(self) -> str:  # pragma: no cover
        """Return repr(self)."""
        return f"Rain Start Event<timestamp={self.timestamp}>"


@dataclass
class WindEvent(Event):
    """Wind event class."""

    _speed: float | None
    _direction: int | None

    @property
    def direction(self) -> Quantity[int]:
        """Return the direction in degrees."""
        return nvl(self._direction, 0) * UNIT_DEGREES

    @property
    def speed(self) -> Quantity[float]:
        """Return the speed in meters per second."""
        return nvl(self._speed, 0) * UNIT_METERS_PER_SECOND

    def __repr__(self) -> str:  # pragma: no cover
        """Return repr(self)."""
        return f"Wind Event<timestamp={self.timestamp}, speed={self.speed}, direction={self.direction.m}°>"


@dataclass
class CustomEvent(Event):
    """Custom event."""

    name: str

    def __repr__(self) -> str:  # pragma: no cover
        """Return repr(self)."""
        return f"Event<timestamp={self.timestamp}, name={self.name}>"
