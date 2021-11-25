"""Mixins for WeatherFlow client and sensors."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

from .enums import PrecipitationType
from .event import LightningStrikeEvent
from .helpers import utc_timestamp_from_epoch


class EventMixin:
    """Event mixin."""

    _listeners: dict[str, list[Callable]] = {}

    def on(  # pylint: disable=invalid-name
        self, event_name: str, callback: Callable
    ) -> Callable:
        """Register an event callback."""
        listeners: list = self._listeners.setdefault(event_name, [])
        listeners.append(callback)

        def unsubscribe() -> None:
            """Unsubscribe listeners."""
            if callback in listeners:
                listeners.remove(callback)

        return unsubscribe

    def emit(self, event_name: str, *args: Any, **kwargs: dict[str, Any]) -> None:
        """Run all callbacks for an event."""
        for listener in self._listeners.get(event_name, []):
            try:
                listener(*args, **kwargs)
            except:  # noqa E722; pylint: disable=bare-except; # pragma: no cover
                pass


class BaseSensorMixin:
    """Base sensor mixin."""

    _battery: float = 0
    _last_report: int | None = None
    _report_interval: int = 0

    @property
    def battery(self) -> float:
        """Return the battery in volts (V)."""
        return self._battery

    @property
    def last_report(self) -> datetime | None:
        """Return last report."""
        return utc_timestamp_from_epoch(self._last_report)

    @property
    def report_interval(self) -> int:
        """Return the report interval in minutes."""
        return self._report_interval


class AirSensorMixin(BaseSensorMixin):
    """Air sensor mixin."""

    _air_temperature: float = 0
    _last_lightning_strike_event: LightningStrikeEvent | None = None
    _lightning_strike_average_distance: float = 0
    _lightning_strike_count: int = 0
    _relative_humidity: float = 0
    _station_pressure: float = 0

    @property
    def air_temperature(self) -> float:
        """Return the air temperature in degrees Celsius."""
        return self._air_temperature

    @property
    def last_lightning_strike_event(self) -> LightningStrikeEvent | None:
        """Return the last lightning strike event."""
        return self._last_lightning_strike_event

    @property
    def lightning_strike_average_distance(self) -> float:
        """Return the lightning strike average distance in kilometers (km)."""
        return self._lightning_strike_average_distance

    @property
    def lightning_strike_count(self) -> int:
        """Return the lightning strike count."""
        return self._lightning_strike_count

    @property
    def relative_humidity(self) -> float:
        """Return the relative humidity percentage."""
        return self._relative_humidity

    @property
    def station_pressure(self) -> float:
        """Return the station pressure in millibars."""
        return self._station_pressure


class SkySensorMixin(BaseSensorMixin):
    """Sky sensor mixin."""

    _illuminance: int = 0
    _precipitation_type: int = 0
    _rain_amount_previous_minute: float = 0
    _solar_radiation: int = 0
    _uv: float = 0
    _wind_average: float = 0
    _wind_direction: int = 0
    _wind_gust: float = 0
    _wind_lull: float = 0
    _wind_sample_interval: int = 0

    @property
    def illuminance(self) -> int:
        """Return the illuminance is lux (lx)."""
        return self._illuminance

    @property
    def precipitation_type(self) -> PrecipitationType:
        """Return the precipitation type."""
        return PrecipitationType(self._precipitation_type)

    @property
    def rain_amount_previous_minute(self) -> float:
        """Return the rain amount over previous minute in millimeters (mm)."""
        return self._rain_amount_previous_minute

    @property
    def solar_radiation(self) -> int:
        """Return the solar radiation in watts per square meter (W/m^2)."""
        return self._solar_radiation

    @property
    def uv(self) -> float:  # pylint: disable=invalid-name
        """Return the uv index."""
        return self._uv

    @property
    def wind_average(self) -> float:
        """Return the wind average in meters per second (m/s)."""
        return self._wind_average

    @property
    def wind_direction(self) -> int:
        """Return the wind direction in degrees."""
        return self._wind_direction

    @property
    def wind_gust(self) -> float:
        """Return the wind gust in meters per second (m/s)."""
        return self._wind_gust

    @property
    def wind_lull(self) -> float:
        """Return the wind lull in meters per second (m/s)."""
        return self._wind_lull

    @property
    def wind_sample_interval(self) -> int:
        """Return wind sample interval in seconds."""
        return self._wind_sample_interval
