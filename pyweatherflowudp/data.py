""".WeatherFlow UDP Data."""
import logging

from pyweatherflowudp.const import (
    EVENT_AIR_DATA,
    EVENT_HUB_STATUS,
    EVENT_RAPID_WIND,
    EVENT_SKY_DATA,
    EVENT_TEMPEST_DATA,
)

_LOGGER = logging.getLogger(__name__)


def station_update_from_udp_frames(state_machine, station_id, data_json):
    """Convert a websocket frame to internal format."""

    if not state_machine.has_device(station_id):
        _LOGGER.debug("Skipping non-configured station: %s", data_json)
        return None, None

    station = state_machine.update(station_id, data_json)

    _LOGGER.debug("Processing station: %s", station)
    processed_station = process_station(station)

    return station_id, processed_station


def process_station(station_data):
    """Process the station json."""

    # TODO: Add formatting and conversion before releasing values
    station_update = {}

    if station_data["event_type"] in EVENT_RAPID_WIND:
        station_update = {
            "time_epoch_rapid_wind": station_data["time_epoch_rapid_wind"],
            "wind_speed": station_data["wind_speed"],
            "wind_direction": station_data["wind_direction"],
        }
    if station_data["event_type"] in EVENT_HUB_STATUS:
        station_update = {
            "hub_firmware_revision": station_data["hub_firmware_revision"],
            "hub_uptime": station_data["hub_uptime"],
            "hub_rssi": station_data["hub_rssi"],
        }
    if station_data["event_type"] in EVENT_SKY_DATA:
        station_update = {
            "time_epoch_sky": station_data["time_epoch_sky"],
            "illuminance": station_data["illuminance"],
            "uv": station_data["uv"],
            "rain_accumulated": station_data["rain_accumulated"],
            "wind_lull": station_data["wind_lull"],
            "wind_avg": station_data["wind_avg"],
            "wind_gust": station_data["wind_gust"],
            "solar_radiation": station_data["solar_radiation"],
            "local_day_rain_accumulation": station_data["local_day_rain_accumulation"],
            "precipitation_type": station_data["precipitation_type"],
            "battery_sky": station_data["battery_sky"],
        }
    if station_data["event_type"] in EVENT_AIR_DATA:
        station_update = {
            "time_epoch_air": station_data["time_epoch_air"],
            "station_pressure": station_data["station_pressure"],
            "air_temperature": station_data["air_temperature"],
            "relative_humidity": station_data["relative_humidity"],
            "lightning_strike_count": station_data["lightning_strike_count"],
            "lightning_strike_avg_distance": station_data[
                "lightning_strike_avg_distance"
            ],
            "battery_air": station_data["battery_air"],
        }
    if station_data["event_type"] in EVENT_TEMPEST_DATA:
        station_update = {
            "time_epoch_tempest": station_data["time_epoch_tempest"],
            "station_pressure": station_data["station_pressure"],
            "air_temperature": station_data["air_temperature"],
            "relative_humidity": station_data["relative_humidity"],
            "lightning_strike_count": station_data["lightning_strike_count"],
            "lightning_strike_avg_distance": station_data[
                "lightning_strike_avg_distance"
            ],
            "illuminance": station_data["illuminance"],
            "uv": station_data["uv"],
            "wind_lull": station_data["wind_lull"],
            "wind_avg": station_data["wind_avg"],
            "wind_gust": station_data["wind_gust"],
            "solar_radiation": station_data["solar_radiation"],
            "local_day_rain_accumulation": station_data["local_day_rain_accumulation"],
            "precipitation_type": station_data["precipitation_type"],
            "battery_sky": station_data["battery_sky"],
            "battery_tempest": station_data["battery_tempest"],
        }

    return station_update


class WeatherflowStationStateMachine:
    """A simple state machine for events."""

    def __init__(self):
        """Init the state machine."""
        self._stations = {}
        self._motion_detected_time = {}

    def has_device(self, station_id):
        """Check to see if a device id is in the state machine."""
        return station_id in self._stations

    def update(self, station_id, new_json):
        """Update an device in the state machine."""
        self._stations.setdefault(station_id, {}).update(new_json)
        return self._stations[station_id]

    def set_motion_detected_time(self, station_id, timestamp):
        """Set device motion start detected time."""
        self._motion_detected_time[station_id] = timestamp

    def get_motion_detected_time(self, station_id):
        """Get device motion start detected time."""
        return self._motion_detected_time.get(station_id)
