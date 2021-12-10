"""WeatherFlow constants."""
import functools
import re

import pint

units = pint.UnitRegistry(
    autoconvert_offset_to_baseunit=True,
    preprocessors=[
        functools.partial(
            re.sub,
            r"(?<=[A-Za-z])(?![A-Za-z])(?<![0-9\-][eE])(?<![0-9\-])(?=[0-9\-])",
            "**",
        ),
        lambda string: string.replace("%", "percent"),
    ],
)
units.define(
    pint.unit.UnitDefinition("percent", "%", (), pint.converters.ScaleConverter(0.01))
)
units.default_format = "P~"

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 50222

EVENT_OBSERVATION_AIR = "obs_air"
EVENT_OBSERVATION_SKY = "obs_sky"
EVENT_OBSERVATION_TEMPEST = "obs_st"
EVENT_RAIN_START = "evt_precip"
EVENT_RAPID_WIND = "rapid_wind"
EVENT_STATUS_DEVICE = "device_status"
EVENT_STATUS_HUB = "hub_status"
EVENT_STRIKE = "evt_strike"

UNIT_DECIBELS = units.dB
UNIT_DEGREES = units.deg
UNIT_DEGREES_CELSIUS = units.degC
UNIT_IRRADIATION = units.W / units.m ** 2
UNIT_KILOGRAMS_PER_CUBIC_METER = units.kg / units.m ** 3
UNIT_KILOMETERS = units.km
UNIT_LUX = units.lx
UNIT_METERS_PER_SECOND = units.m / units.sec
UNIT_MILLIBARS = units.mbar
UNIT_MILLIMETERS = units.mm
UNIT_MILLIMETERS_PER_MINUTE = units.mm / units.min
UNIT_MILLIMETERS_PER_HOUR = units.mm / units.hr
UNIT_MINUTES = units.min
UNIT_PERCENT = units.percent
UNIT_SECONDS = units.sec
UNIT_VOLTS = units.V
