"""Calc functions."""
from __future__ import annotations

import psychrolib
from pint import Quantity

from .const import (
    UNIT_DEGREES_CELSIUS,
    UNIT_KILOGRAMS_PER_CUBIC_METER,
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


def heat_index(
    air_temperature: Quantity[float], relative_humidity: Quantity[float]
) -> Quantity[float] | None:
    """Calculate the heat index.

    Only temperatures >= 80°F (26.66°C) have a heat index.
    """
    temp_fahrenheit = air_temperature.to("degF").m

    if temp_fahrenheit < 80:
        return None

    rh_percent = relative_humidity.m * (
        1 if relative_humidity.u == UNIT_PERCENT or relative_humidity.m > 1 else 100
    )

    heat_idx = 0.5 * (
        temp_fahrenheit + 61.0 + ((temp_fahrenheit - 68.0) * 1.2) + (rh_percent * 0.094)
    )
    if (heat_idx + temp_fahrenheit) / 2 >= 80:
        heat_idx = (
            -42.379
            + 2.04901523 * temp_fahrenheit
            + 10.14333127 * rh_percent
            - 0.22475541 * temp_fahrenheit * rh_percent
            - 0.00683783 * temp_fahrenheit * temp_fahrenheit
            - 0.05481717 * rh_percent * rh_percent
            + 0.00122874 * temp_fahrenheit * temp_fahrenheit * rh_percent
            + 0.00085282 * temp_fahrenheit * rh_percent * rh_percent
            - 0.00000199 * temp_fahrenheit * temp_fahrenheit * rh_percent * rh_percent
        )
        if rh_percent < 13 and (80 <= temp_fahrenheit <= 112):
            heat_idx -= ((13 - rh_percent) / 4) * (
                (17 - abs(temp_fahrenheit - 95.0)) / 17
            ) ** 0.5
        elif rh_percent > 85 and (80 <= temp_fahrenheit <= 87):
            heat_idx += ((rh_percent - 85) / 10) * ((87 - temp_fahrenheit) / 5)
    return (heat_idx * units.degF).to(air_temperature.u)


def sea_level_pressure(
    station_pressure: Quantity[float],
    altitude: Quantity[float],
    air_temperature: Quantity[float],
) -> Quantity[float]:
    """Calculate the sea level pressure."""
    return (
        psychrolib.GetSeaLevelPressure(
            station_pressure.to("Pa").m,
            altitude.to("m").m,
            air_temperature.to("degC").m,
        )
        * units.Pa
    ).to(station_pressure.u)


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
