"""Constant definitions for SecSpy Wrapper."""

DEVICE_UPDATE_INTERVAL_SECONDS = 60
SOCKET_CHECK_INTERVAL_SECONDS = 120

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 50222

EVENT_RAPID_WIND = "rapid_wind"
EVENT_HUB_STATUS = "hub_status"
EVENT_DEVICE_STATUS = "device_status"
EVENT_AIR_DATA = "obs_air"
EVENT_SKY_DATA = "obs_sky"
EVENT_TEMPEST_DATA = "obs_st"
EVENT_PRECIP_START = "evt_precip"
EVENT_STRIKE = "evt_strike"
SUPPORTED_EVENTS = [
    EVENT_DEVICE_STATUS,
    EVENT_HUB_STATUS,
    EVENT_RAPID_WIND,
    EVENT_AIR_DATA,
    EVENT_SKY_DATA,
    EVENT_TEMPEST_DATA,
    EVENT_STRIKE,
    EVENT_PRECIP_START,
]

PROCESSED_EVENT_EMPTY = {
    "time_epoch_rapid_wind": None,
    "time_epoch_sky": None,
    "time_epoch_air": None,
    "time_epoch_tempest": None,
    "wind_speed": 0,
    "wind_bearing": 0,
    "wind_direction": None,
    "station_pressure": 0,
    "air_temperature": 0,
    "relative_humidity": 0,
    "lightning_strike_count": 0,
    "lightning_strike_avg_distance": 0,
    "battery_air": 0,
    "battery_sky": 0,
    "battery_tempest": 0,
    "illuminance": 0,
    "uv": 0,
    "rain_accumulated": 0,
    "wind_lull": 0,
    "wind_avg": 0,
    "wind_gust": 0,
    "solar_radiation": 0,
    "local_day_rain_accumulation": 0,
    "precipitation_type": 0,
    "hub_firmware_revision": None,
    "hub_uptime": None,
    "hub_rssi": 0,
    "dewpoint": 0,
    "heatindex": 0,
}

UNIT_SYSTEM_METRIC = "metric"
UNIT_SYSTEM_IMPERIAL = "imperial"
