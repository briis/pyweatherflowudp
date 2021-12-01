"""Mixins for WeatherFlow client and sensors."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Callable

import metpy.calc as mpcalc
from pint import Quantity

from .const import (
    UNIT_DEGREES,
    UNIT_DEGREES_CELSIUS,
    UNIT_IRRADIATION,
    UNIT_KILOMETERS,
    UNIT_LUX,
    UNIT_METERS_PER_SECOND,
    UNIT_MILLIBARS,
    UNIT_MILLIMETERS_PER_MINUTE,
    UNIT_MINUTES,
    UNIT_PERCENT,
    UNIT_VOLTS,
)
from .enums import PrecipitationType
from .event import LightningStrikeEvent, RainStartEvent, WindEvent
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
            listener(*args, **kwargs)


class BaseSensorMixin:
    """Base sensor mixin."""

    _battery: float = 0
    _last_report: int | None = None
    _report_interval: int = 0

    @property
    def battery(self) -> Quantity[float]:
        """Return the battery in volts (V)."""
        return self._battery * UNIT_VOLTS

    @property
    def last_report(self) -> datetime | None:
        """Return last report."""
        return utc_timestamp_from_epoch(self._last_report)

    @property
    def report_interval(self) -> Quantity[int]:
        """Return the report interval in minutes."""
        return self._report_interval * UNIT_MINUTES


class AirSensorMixin(BaseSensorMixin):
    """Air sensor mixin."""

    _air_temperature: float = 0
    _last_lightning_strike_event: LightningStrikeEvent | None = None
    _lightning_strike_average_distance: float = 0
    _lightning_strike_count: int = 0
    _relative_humidity: float = 0
    _station_pressure: float = 0

    @property
    def air_temperature(self) -> Quantity[float]:
        """Return the air temperature in degrees Celsius (°C)."""
        return self._air_temperature * UNIT_DEGREES_CELSIUS

    @property
    def last_lightning_strike_event(self) -> LightningStrikeEvent | None:
        """Return the last lightning strike event."""
        return self._last_lightning_strike_event

    @property
    def lightning_strike_average_distance(
        self,
    ) -> Quantity[float]:
        """Return the lightning strike average distance in kilometers (km)."""
        return self._lightning_strike_average_distance * UNIT_KILOMETERS

    @property
    def lightning_strike_count(self) -> int:
        """Return the lightning strike count."""
        return self._lightning_strike_count

    @property
    def relative_humidity(self) -> Quantity[float]:
        """Return the relative humidity percentage."""
        return self._relative_humidity * UNIT_PERCENT

    @property
    def station_pressure(self) -> Quantity[float]:
        """Return the station pressure in millibars (mbar)."""
        return self._station_pressure * UNIT_MILLIBARS

    # Derived metrics

    @property
    def air_density(self) -> Quantity[float]:
        """Return the calculated air density in kilograms per cubic meter (kg/m³)."""
        return mpcalc.density(self.station_pressure, self.air_temperature, 0)

    @property
    def delta_t(self) -> Quantity[float]:
        """Return the calculated delta t in delta degrees Celsius (Δ°C)."""
        return self.air_temperature - self.wet_bulb_temperature

    @property
    def dew_point_temperature(self) -> Quantity[float]:
        """Return the calculated dew point temperature in degrees Celsius (°C)."""
        return mpcalc.dewpoint_from_relative_humidity(
            self.air_temperature, self.relative_humidity
        )

    @property
    def heat_index(self) -> Quantity[float]:
        """Return the calculated heat index in degrees Celsius (°C)."""
        return mpcalc.heat_index(
            self.air_temperature, self.relative_humidity, mask_undefined=False
        )[0].to(UNIT_DEGREES_CELSIUS)

    def sea_level_pressure(self, height: Quantity[float]) -> Quantity[float]:
        """Return the calculated sea level pressure in millibars (mbar)."""
        return mpcalc.altimeter_to_sea_level_pressure(
            self.station_pressure, height, self.air_temperature
        )

    @property
    def vapor_pressure(self) -> Quantity[float]:
        """Return the calculated vapor pressure in millibars (mbar)."""
        return (
            self.relative_humidity
            * mpcalc.saturation_vapor_pressure(self.air_temperature)
            / self.relative_humidity.u
        )

    @property
    def wet_bulb_temperature(self) -> Quantity[float]:
        """Return the calculated wet bulb temperature in degrees Celsius (°C)."""
        return mpcalc.wet_bulb_temperature(
            self.station_pressure, self.air_temperature, self.dew_point_temperature
        )


class SkySensorMixin(BaseSensorMixin):
    """Sky sensor mixin."""

    _illuminance: int = 0
    _last_rain_start_event: RainStartEvent | None = None
    _last_wind_event: WindEvent | None = None
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
    def illuminance(self) -> Quantity[int]:
        """Return the illuminance is lux (lx)."""
        return self._illuminance * UNIT_LUX

    @property
    def last_rain_start_event(self) -> RainStartEvent | None:
        """Return the last rain start event."""
        return self._last_rain_start_event

    @property
    def last_wind_event(self) -> WindEvent | None:
        """Return the last wind event."""
        return self._last_wind_event

    @property
    def precipitation_type(self) -> PrecipitationType:
        """Return the precipitation type."""
        return PrecipitationType(self._precipitation_type)

    @property
    def rain_amount_previous_minute(
        self,
    ) -> Quantity[float]:
        """Return the rain amount over previous minute in millimeters (mm/min)."""
        return self._rain_amount_previous_minute * UNIT_MILLIMETERS_PER_MINUTE

    @property
    def solar_radiation(self) -> Quantity[int]:
        """Return the solar radiation in watts per square meter (W/m²)."""
        return self._solar_radiation * UNIT_IRRADIATION

    @property
    def uv(self) -> float:  # pylint: disable=invalid-name
        """Return the uv index."""
        return self._uv

    @property
    def wind_average(self) -> Quantity[float]:
        """Return the wind average in meters per second (m/s)."""
        return self._wind_average * UNIT_METERS_PER_SECOND

    @property
    def wind_direction(self) -> Quantity[int]:
        """Return the wind direction in degrees."""
        return self._wind_direction * UNIT_DEGREES

    @property
    def wind_gust(self) -> Quantity[float]:
        """Return the wind gust in meters per second (m/s)."""
        return self._wind_gust * UNIT_METERS_PER_SECOND

    @property
    def wind_lull(self) -> Quantity[float]:
        """Return the wind lull in meters per second (m/s)."""
        return self._wind_lull * UNIT_METERS_PER_SECOND

    @property
    def wind_sample_interval(self) -> Quantity[int]:
        """Return wind sample interval in seconds."""
        return self._wind_sample_interval * UNIT_MINUTES

    @property
    def wind_speed(self) -> Quantity[float]:
        """Return the most recent wind speed in meters per second (m/s)."""
        return (
            self.wind_average
            if self._last_wind_event is None
            or (self._last_report or 0) > self._last_wind_event.epoch
            else self._last_wind_event.speed
        )
