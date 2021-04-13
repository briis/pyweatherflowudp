""".WeatherFlow UDP Data."""
import logging
import math

from pyweatherflowudp.const import (
    EVENT_AIR_DATA,
    EVENT_HUB_STATUS,
    EVENT_RAPID_WIND,
    EVENT_SKY_DATA,
    EVENT_TEMPEST_DATA,
    UNIT_SYSTEM_METRIC,
)
_LOGGER = logging.getLogger(__name__)


def station_update_from_udp_frames(state_machine, station_id, unit_system, data_json):
    """Convert a websocket frame to internal format."""

    if not state_machine.has_device(station_id):
        _LOGGER.debug("Skipping non-configured station: %s", data_json)
        return None, None

    station = state_machine.update(station_id, data_json)

    _LOGGER.debug("Processing station: %s", station)
    processed_station = process_station(station, unit_system)

    return station_id, processed_station


def process_station(station_data, unit_system):
    """Process the station json."""

    cnv = WeatherFunctions(unit_system)
    station_update = {}

    if station_data["event_type"] in EVENT_RAPID_WIND:
        station_update = {
            "time_epoch_rapid_wind": station_data["time_epoch_rapid_wind"],
            "wind_speed": cnv.windspeed(station_data["wind_speed"]),
            "wind_bearing": station_data["wind_bearing"],
            "wind_direction": cnv.winddirection_string(station_data["wind_bearing"]),
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
            "rain_accumulated": cnv.rainvolume(station_data["rain_accumulated"]),
            "wind_avg": cnv.windspeed(station_data["wind_avg"]),
            "wind_gust": cnv.windspeed(station_data["wind_gust"]),
            "wind_lull": cnv.windspeed(station_data["wind_lull"]),
            "wind_bearing": station_data["wind_bearing"],
            "wind_direction": cnv.winddirection_string(station_data["wind_bearing"]),
            "solar_radiation": station_data["solar_radiation"],
            "local_day_rain_accumulation": cnv.rainvolume(station_data["local_day_rain_accumulation"]),
            "precipitation_type": station_data["precipitation_type"],
            "battery_sky": station_data["battery_sky"],
        }
    if station_data["event_type"] in EVENT_AIR_DATA:
        station_update = {
            "time_epoch_air": station_data["time_epoch_air"],
            "station_pressure": cnv.pressure(station_data["station_pressure"]),
            "air_temperature": station_data["air_temperature"],
            "relative_humidity": station_data["relative_humidity"],
            "lightning_strike_count": station_data["lightning_strike_count"],
            "lightning_strike_avg_distance": cnv.distance(station_data[
                "lightning_strike_avg_distance"
            ]),
            "battery_air": station_data["battery_air"],
            "dewpoint": cnv.dewpoint(station_data["air_temperature"], station_data["relative_humidity"]),
            "heatindex": cnv.heatindex(station_data["air_temperature"], station_data["relative_humidity"]),
        }
    if station_data["event_type"] in EVENT_TEMPEST_DATA:
        station_update = {
            "time_epoch_tempest": station_data["time_epoch_tempest"],
            "station_pressure": cnv.pressure(station_data["station_pressure"]),
            "air_temperature": station_data["air_temperature"],
            "relative_humidity": station_data["relative_humidity"],
            "lightning_strike_count": station_data["lightning_strike_count"],
            "lightning_strike_avg_distance": cnv.distance(station_data[
                "lightning_strike_avg_distance"
            ]),
            "illuminance": station_data["illuminance"],
            "uv": station_data["uv"],
            "wind_avg": cnv.windspeed(station_data["wind_avg"]),
            "wind_gust": cnv.windspeed(station_data["wind_gust"]),
            "wind_lull": cnv.windspeed(station_data["wind_lull"]),
            "wind_bearing": station_data["wind_bearing"],
            "wind_direction": cnv.winddirection_string(station_data["wind_bearing"]),
            "solar_radiation": station_data["solar_radiation"],
            "local_day_rain_accumulation": cnv.rainvolume(station_data["local_day_rain_accumulation"]),
            "precipitation_type": station_data["precipitation_type"],
            "battery_sky": station_data["battery_sky"],
            "battery_tempest": station_data["battery_tempest"],
            "dewpoint": cnv.dewpoint(station_data["air_temperature"], station_data["relative_humidity"]),
            "heatindex": cnv.heatindex(station_data["air_temperature"], station_data["relative_humidity"]),
        }

    return station_update

class WeatherFunctions:
    """Contains a set of Weather Formulas."""

    def __init__(self, unit_system):
        self._unit_system = unit_system

    def heatindex(self, temperature, humidity):
        """Returns the calculated Heat Index in Celcius."""
        T = temperature * 9/5 + 32 #Convert to Fahrenheit
        RH = humidity
        c1 = -42.379
        c2 = 2.04901523
        c3 = 10.14333127
        c4 = -0.22475541
        c5 = -6.83783e-3
        c6 = -5.481717e-2
        c7 = 1.22874e-3
        c8 = 8.5282e-4
        c9 = -1.99e-6

        # try simplified formula first (used for HI < 80)
        HI = 0.5 * (T + 61. + (T - 68.) * 1.2 + RH * 0.094)

        if HI >= 80:
            # use Rothfusz regression
            HI = math.fsum([
                c1,
                c2 * T,
                c3 * RH,
                c4 * T * RH,
                c5 * T**2,
                c6 * RH**2,
                c7 * T**2 * RH,
                c8 * T * RH**2,
                c9 * T**2 * RH**2,
            ])

        return round((HI - 32) * 5/9, 1)

    def dewpoint(self, temperature, humidity):
        """ Returns Dew Point in Celcius """
        return round(243.04*(math.log(humidity/100)+((17.625*temperature)/(243.04+temperature)))/(17.625-math.log(humidity/100)-((17.625*temperature)/(243.04+temperature))),1)

    def windchill(self, wind_speed, temperature):
        """ Returns Wind Chill in Celcius """
        if wind_speed < 1.3:
            return round(temperature,1)

        windKmh = wind_speed * 3.6
        return round(13.12 + (0.6215 * temperature) - (11.37 * math.pow(windKmh, 0.16)) + (0.3965 * temperature * math.pow(windKmh, 0.16)), 1)

    def feelslike(self, temperature, wind_chill, heat_index):
        """ Returns the Feels Like Temperature in Celcius """
        if temperature > 26.666666667:
            return heat_index
        elif temperature < 10:
            return wind_chill
        else:
            return round(temperature,1)

    def distance(self, value):
        """Return value based on unit system."""
        if self._unit_system in UNIT_SYSTEM_METRIC:
            return value

        return round(value * 0.621371192, 1)

    def pressure(self, value):
        """Return value based on unit system."""
        if self._unit_system in UNIT_SYSTEM_METRIC:
            return value

        return round(value * 0.0295299801647, 3)

    def rainvolume(self, value):
        """Return value based on unit system."""
        if value is None:
            return None

        if self._unit_system in UNIT_SYSTEM_METRIC:
            return value

        return round(value * 0.0393700787, 1)

    def windspeed(self, value):
        """Return value based on unit system."""
        if self._unit_system in UNIT_SYSTEM_METRIC:
            return value

        return round(value * 2.2369362921, 1)

    def winddirection_string(self, bearing):
        """Return a Wind Direction String from a degree bearing."""
        direction_array = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW','N']
        direction = direction_array[int((bearing + 11.25) / 22.5)]
        return direction

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
