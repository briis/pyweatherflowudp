"""Calc functions."""
from __future__ import annotations

import psychrolib
from pint import Quantity

from .const import (
    UNIT_DEGREES_CELSIUS,
    UNIT_KILOGRAMS_PER_CUBIC_METER,
    UNIT_METERS,
    UNIT_MILLIBARS,
    UNIT_PERCENT,
    units,
)

psychrolib.SetUnitSystem(psychrolib.SI)


def air_density(
    air_temperature: Quantity[float], station_pressure: Quantity[float]
) -> Quantity[float]:
    """Calculate the air density in kilograms per cubic meter (kg/m³)."""
    return (
        psychrolib.GetDryAirDensity(
            air_temperature.to("degC").m, station_pressure.to("Pa").m
        )
        * UNIT_KILOGRAMS_PER_CUBIC_METER
    )


def cloud_base(
    air_temperature: Quantity[float],
    relative_humidity: Quantity[float],
    altitude: Quantity[float],
) -> Quantity[float]:
    """Calculate the estimated altitude above mean sea level (AMSL) to the cloud base.

    Reference:
        https://holfuy.com/en/support/cloud-base-calculations
    """
    return (
        (
            (
                air_temperature.to("degC").m
                - dew_point_temperature(air_temperature, relative_humidity).to("degC").m
            )
            * 126
            + altitude.to("m").m
        )
        * UNIT_METERS
    ).to(altitude.u)


def dew_point_temperature(
    air_temperature: Quantity[float], relative_humidity: Quantity[float]
) -> Quantity[float]:
    """Calculate the dew point temperature."""
    return (
        psychrolib.GetTDewPointFromRelHum(
            air_temperature.to("degC").m,
            relative_humidity.m
            / (
                100
                if relative_humidity.u == UNIT_PERCENT or relative_humidity.m > 1
                else 1
            ),
        )
        * UNIT_DEGREES_CELSIUS
    ).to(air_temperature.u)


def feels_like_temperature(
    air_temperature: Quantity[float],
    relative_humidity: Quantity[float],
    wind_speed: Quantity[float],
) -> Quantity[float] | None:
    """Calculate the "feels like" temperature."""
    # fmt: off
    if (temp := heat_index(air_temperature=air_temperature, relative_humidity=relative_humidity)) is not None:
        return temp
    if (temp := wind_chill(air_temperature=air_temperature, wind_speed=wind_speed)) is not None:
        return temp
    # fmt: on
    return air_temperature


def freezing_level(
    air_temperature: Quantity[float], altitude: Quantity[float]
) -> Quantity[float]:
    """Calculate the estimated altitude above mean sea level (AMSL) where the temperature is at the freezing point (0°C/32°F).

    References:
        https://github.com/briis/hass-weatherflow2mqtt/issues/131
        https://community.home-assistant.io/t/local-offline-self-hosted-weather-forecast/349135/16
    """
    return ((air_temperature.to("degC").m * 192 + altitude.to("m").m) * UNIT_METERS).to(
        altitude.u
    )


def heat_index(
    air_temperature: Quantity[float], relative_humidity: Quantity[float]
) -> Quantity[float] | None:
    """Calculate the heat index.

    Only temperatures >= 80°F (26.66°C) and relative humidity >= 40% have a heat index.
    """
    temp_fahrenheit = air_temperature.to("degF").m
    rh_percent = relative_humidity.m * (
        1 if relative_humidity.u == UNIT_PERCENT or relative_humidity.m > 1 else 100
    )
    if temp_fahrenheit < 80 or rh_percent < 40:
        return None

    heat_idx = (
        -42.379
        + 2.04901523 * temp_fahrenheit
        + 10.14333127 * rh_percent
        - 0.22475541 * temp_fahrenheit * rh_percent
        - 0.00683783 * temp_fahrenheit**2
        - 0.05481717 * rh_percent**2
        + 0.00122874 * temp_fahrenheit**2 * rh_percent
        + 0.00085282 * temp_fahrenheit * rh_percent**2
        - 0.00000199 * temp_fahrenheit**2 * rh_percent**2
    )

    return (heat_idx * units.degF).to(air_temperature.u)


@units.wraps(units.millibar, (units.millibar, units.meter))
def sea_level_pressure(
    station_pressure: Quantity[float], altitude: Quantity[float]
) -> Quantity[float]:
    """Calculate the sea level pressure in millibars (mbar).

    https://weatherflow.github.io/Tempest/api/derived-metric-formulas.html#sea-level-pressure
    """
    standard_sea_level_pressure = 1013.25  # mbar
    dry_air_gas_constant = 287.05  # J/(kg*K)
    standard_atmosphere_lapse_rate = 0.0065  # K/m
    gravity = 9.80665  # m/s**2
    standard_sea_level_temperature = 288.15  # K
    return station_pressure * (
        1
        + (standard_sea_level_pressure / station_pressure)
        ** (dry_air_gas_constant * standard_atmosphere_lapse_rate / gravity)
        * (standard_atmosphere_lapse_rate * altitude / standard_sea_level_temperature)
    ) ** (gravity / (dry_air_gas_constant * standard_atmosphere_lapse_rate))


def vapor_pressure(
    air_temperature: Quantity[float], relative_humidity: Quantity[float]
) -> Quantity[float]:
    """Calculate the vapor pressure in millibars (mbar)."""
    return (
        psychrolib.GetVapPresFromRelHum(
            air_temperature.to("degC").m,
            relative_humidity.m
            / (
                100
                if relative_humidity.u == UNIT_PERCENT or relative_humidity.m > 1
                else 1
            ),
        )
        * UNIT_MILLIBARS
    )


def wet_bulb_temperature(
    air_temperature: Quantity[float],
    relative_humidity: Quantity[float],
    station_pressure: Quantity[float],
) -> Quantity[float]:
    """Calculate the wet bulb temperature."""
    return (
        psychrolib.GetTWetBulbFromRelHum(
            air_temperature.to("degC").m,
            relative_humidity.m / (100 if relative_humidity.m > 1 else 1),
            station_pressure.to("Pa").m,
        )
        * UNIT_DEGREES_CELSIUS
    ).to(air_temperature.u)


def wind_chill(
    air_temperature: Quantity[float], wind_speed: Quantity[float]
) -> Quantity[float] | None:
    """Calculate the wind chill temperature.

    Only temperatures <= 50°F (10°C) and winds >= 3mph (1.34112 m/s) have a wind chill.
    """
    temp_fahrenheit = air_temperature.to("degF").m
    wind_mph = wind_speed.to("mph").m
    if temp_fahrenheit > 50 or wind_mph < 3:
        return None

    return (
        (
            35.74
            + (0.6215 * temp_fahrenheit)
            - (35.75 * pow(wind_mph, 0.16))
            + (0.4275 * temp_fahrenheit * pow(wind_mph, 0.16))
        )
        * units.degF
    ).to(air_temperature.u)
