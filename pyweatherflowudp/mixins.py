"""Mixins for WeatherFlow client and sensors."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Callable

from pint import Quantity

from .calc import (
    air_density,
    dew_point_temperature,
    heat_index,
    sea_level_pressure,
    vapor_pressure,
    wet_bulb_temperature,
)
from .const import (
    UNIT_DEGREES,
    UNIT_DEGREES_CELSIUS,
    UNIT_IRRADIATION,
    UNIT_KILOMETERS,
    UNIT_LUX,
    UNIT_METERS_PER_SECOND,
    UNIT_MILLIBARS,
    UNIT_MILLIMETERS,
    UNIT_MILLIMETERS_PER_HOUR,
    UNIT_MILLIMETERS_PER_MINUTE,
    UNIT_MINUTES,
    UNIT_PERCENT,
    UNIT_SECONDS,
    UNIT_VOLTS,
)
from .enums import PrecipitationType
from .event import LightningStrikeEvent, RainStartEvent, WindEvent
from .helpers import degrees_to_cardinal, nvl, utc_timestamp_from_epoch, value_as_unit

_LOGGER = logging.getLogger(__name__)


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

    _battery: float | None = 0
    _last_report: int | None = None
    _report_interval: int | None = 0

    @property
    def battery(self) -> Quantity[float] | None:
        """Return the battery in volts (V)."""
        return value_as_unit(self._battery, UNIT_VOLTS)

    @property
    def last_report(self) -> datetime | None:
        """Return last report."""
        return utc_timestamp_from_epoch(self._last_report)

    @property
    def report_interval(self) -> Quantity[int]:
        """Return the report interval in minutes."""
        return nvl(self._report_interval, 0) * UNIT_MINUTES


class AirSensorMixin(BaseSensorMixin):
    """Air sensor mixin."""

    _air_temperature: float | None = None
    _last_lightning_strike_event: LightningStrikeEvent | None = None
    _lightning_strike_average_distance: float | None = None
    _lightning_strike_count: int | None = None
    _relative_humidity: float | None = None
    _station_pressure: float | None = None

    @property
    def air_temperature(self) -> Quantity[float] | None:
        """Return the air temperature in degrees Celsius (°C)."""
        return value_as_unit(self._air_temperature, UNIT_DEGREES_CELSIUS)

    @property
    def last_lightning_strike_event(self) -> LightningStrikeEvent | None:
        """Return the last lightning strike event."""
        return self._last_lightning_strike_event

    @property
    def lightning_strike_average_distance(self) -> Quantity[float] | None:
        """Return the lightning strike average distance in kilometers (km)."""
        return value_as_unit(self._lightning_strike_average_distance, UNIT_KILOMETERS)

    @property
    def lightning_strike_count(self) -> int | None:
        """Return the lightning strike count."""
        return value_as_unit(self._lightning_strike_count)

    @property
    def relative_humidity(self) -> Quantity[float] | None:
        """Return the relative humidity percentage."""
        return value_as_unit(self._relative_humidity, UNIT_PERCENT)

    @property
    def station_pressure(self) -> Quantity[float] | None:
        """Return the station pressure in millibars (mbar)."""
        return value_as_unit(self._station_pressure, UNIT_MILLIBARS)

    # Derived metrics

    @property
    def air_density(self) -> Quantity[float] | None:
        """Return the calculated air density in kilograms per cubic meter (kg/m³)."""
        if None in (self.air_temperature, self.station_pressure):
            return None
        return air_density(self.air_temperature, self.station_pressure)

    @property
    def delta_t(self) -> Quantity[float] | None:
        """Return the calculated delta t in delta degrees Celsius (Δ°C)."""
        if self.air_temperature is None or self.wet_bulb_temperature is None:
            return None
        return self.air_temperature - self.wet_bulb_temperature

    @property
    def dew_point_temperature(self) -> Quantity[float] | None:
        """Return the calculated dew point temperature in degrees Celsius (°C)."""
        if None in (self.air_temperature, self.relative_humidity):
            return None
        return dew_point_temperature(self.air_temperature, self.relative_humidity)

    @property
    def heat_index(self) -> Quantity[float] | None:
        """Return the calculated heat index in degrees Celsius (°C)."""
        if None in (self.air_temperature, self.relative_humidity):
            return None
        return heat_index(self.air_temperature, self.relative_humidity)

    @property
    def vapor_pressure(self) -> Quantity[float] | None:
        """Return the calculated vapor pressure in millibars (mbar)."""
        if None in (self.air_temperature, self.relative_humidity):
            return None
        return vapor_pressure(self.air_temperature, self.relative_humidity)

    @property
    def wet_bulb_temperature(self) -> Quantity[float] | None:
        """Return the calculated wet bulb temperature in degrees Celsius (°C)."""
        if None in (
            self.air_temperature,
            self.relative_humidity,
            self.station_pressure,
        ):
            return None
        return wet_bulb_temperature(
            self.air_temperature, self.relative_humidity, self.station_pressure
        )

    def calculate_sea_level_pressure(
        self, height: Quantity[float]
    ) -> Quantity[float] | None:
        """Calculate the sea level pressure in millibars (mbar) from a specified height."""
        if None in (self.air_temperature, self.station_pressure):
            return None
        return sea_level_pressure(self.station_pressure, height, self.air_temperature)


class SkySensorMixin(BaseSensorMixin):
    """Sky sensor mixin."""

    _illuminance: int | None = None
    _last_rain_start_event: RainStartEvent | None = None
    _last_wind_event: WindEvent | None = None
    _precipitation_type: int | None = None
    _rain_accumulation_previous_minute: float | None = None
    _solar_radiation: int | None = None
    _uv: float | None = None
    _wind_average: float | None = None
    _wind_direction: int | None = None
    _wind_gust: float | None = None
    _wind_lull: float | None = None
    _wind_sample_interval: int | None = None

    @property
    def illuminance(self) -> Quantity[int] | None:
        """Return the illuminance is lux (lx)."""
        return value_as_unit(self._illuminance, UNIT_LUX)

    @property
    def last_rain_start_event(self) -> RainStartEvent | None:
        """Return the last rain start event."""
        return self._last_rain_start_event

    @property
    def last_wind_event(self) -> WindEvent | None:
        """Return the last wind event."""
        return self._last_wind_event

    @property
    def precipitation_type(self) -> PrecipitationType | None:
        """Return the precipitation type."""
        if (val := value_as_unit(self._precipitation_type)) is None:
            return None
        return PrecipitationType(val)

    @property
    def rain_accumulation_previous_minute(self) -> Quantity[float] | None:
        """Return the rain accumulation from the previous minute in millimeters."""
        return value_as_unit(self._rain_accumulation_previous_minute, UNIT_MILLIMETERS)

    @property
    def rain_amount_previous_minute(self) -> Quantity[float] | None:
        """**Return the rain amount over previous minute in millimeters (mm/min).

        **This property has been deprecated. Please use `rain_accumulation_previous_minute`
        for an accumulation amount or `rain_rate` for an hourly intensity.
        """
        _LOGGER.warning(
            "The property 'rain_amount_previous_minute' has been deprecated due to "
            "inconsistent naming with the property and the units. Please use either "
            "`rain_accumulation_previous_minute` for a rain accumulation amount or "
            "`rain_rate` for an hourly intensity of rain."
        )
        return value_as_unit(
            self._rain_accumulation_previous_minute, UNIT_MILLIMETERS_PER_MINUTE
        )

    @property
    def rain_rate(self) -> Quantity[float] | None:
        """Return the rain rate in millimeters per hour (mm/hr).

        Based on the rain accumulation from the previous minute.
        """
        if self._rain_accumulation_previous_minute is None:
            return None
        return self._rain_accumulation_previous_minute * 60 * UNIT_MILLIMETERS_PER_HOUR

    @property
    def solar_radiation(self) -> Quantity[int] | None:
        """Return the solar radiation in watts per square meter (W/m²)."""
        return value_as_unit(self._solar_radiation, UNIT_IRRADIATION)

    @property
    def uv(self) -> float | None:  # pylint: disable=invalid-name
        """Return the uv index."""
        return value_as_unit(self._uv)

    @property
    def wind_average(self) -> Quantity[float] | None:
        """Return the wind average in meters per second (m/s)."""
        return value_as_unit(self._wind_average, UNIT_METERS_PER_SECOND)

    @property
    def wind_direction(self) -> Quantity[int] | None:
        """Return the wind direction in degrees."""
        return value_as_unit(self._wind_direction, UNIT_DEGREES)

    @property
    def wind_direction_cardinal(self) -> str | None:
        """Return the wind direction cardinality."""
        if self._wind_direction is None:
            return None
        return degrees_to_cardinal(self._wind_direction)

    @property
    def wind_gust(self) -> Quantity[float] | None:
        """Return the wind gust in meters per second (m/s)."""
        return value_as_unit(self._wind_gust, UNIT_METERS_PER_SECOND)

    @property
    def wind_lull(self) -> Quantity[float] | None:
        """Return the wind lull in meters per second (m/s)."""
        return value_as_unit(self._wind_lull, UNIT_METERS_PER_SECOND)

    @property
    def wind_sample_interval(self) -> Quantity[int] | None:
        """Return wind sample interval in seconds."""
        return value_as_unit(self._wind_sample_interval, UNIT_SECONDS)

    @property
    def wind_speed(self) -> Quantity[float] | None:
        """Return the most recent wind speed in meters per second (m/s)."""
        return (
            self.wind_average
            if self._last_wind_event is None
            or nvl(self._last_report, 0) > self._last_wind_event.epoch
            else self._last_wind_event.speed
        )
