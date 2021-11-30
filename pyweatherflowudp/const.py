"""WeatherFlow constants."""
from metpy.units import units

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
UNIT_MILLIMETERS_PER_MINUTE = units.mm / units.min
UNIT_MINUTES = units.min
UNIT_PERCENT = units.percent
UNIT_SECONDS = units.sec
UNIT_VOLTS = units.V
