"""Test devices."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from _pytest.logging import LogCaptureFixture

from pyweatherflowudp.const import (
    UNIT_DECIBELS,
    UNIT_DEGREES,
    UNIT_DEGREES_CELSIUS,
    UNIT_IRRADIATION,
    UNIT_KILOGRAMS_PER_CUBIC_METER,
    UNIT_KILOMETERS,
    UNIT_LUX,
    UNIT_METERS_PER_SECOND,
    UNIT_MILLIBARS,
    UNIT_MILLIMETERS_PER_MINUTE,
    UNIT_MINUTES,
    UNIT_PERCENT,
    UNIT_SECONDS,
    UNIT_VOLTS,
    units,
)
from pyweatherflowudp.device import (
    DATA_OBSERVATIONS,
    EVENT_LOAD_COMPLETE,
    AirDevice,
    HubDevice,
    SkyDevice,
    TempestDevice,
)
from pyweatherflowudp.enums import PrecipitationType

SERIAL_NUMBER = "00000001"
HUB_SERIAL_NUMBER = f"HB-{SERIAL_NUMBER}"
AIR_SERIAL_NUMBER = f"AR-{SERIAL_NUMBER}"
SKY_SERIAL_NUMBER = f"SK-{SERIAL_NUMBER}"
TEMPEST_SERIAL_NUMBER = f"ST-{SERIAL_NUMBER}"


def test_hub_device(hub_status: dict[str, Any]) -> None:
    """Test handling of a hub device."""
    device = HubDevice(serial_number=HUB_SERIAL_NUMBER, data=hub_status)
    assert device.model == "Hub"
    assert device.serial_number == HUB_SERIAL_NUMBER

    assert not device.load_complete
    device.parse_message(hub_status)
    assert device.load_complete
    assert device.rssi == -62 * UNIT_DECIBELS
    assert device.firmware_revision == "35"
    assert device.timestamp == datetime.fromtimestamp(1495724691, timezone.utc)
    assert device.up_since == datetime.fromtimestamp(1495724691 - 1670133, timezone.utc)
    assert device.uptime == 1670133 * UNIT_SECONDS
    assert device.reset_flags == ["Brownout reset", "PIN reset", "Power reset"]

    hub_status.update({"timestamp": 1495725691})
    device.parse_message(hub_status)
    assert device.timestamp == datetime.fromtimestamp(1495725691, timezone.utc)


def test_air_device(obs_air: dict[str, Any]) -> None:
    """Test handling of an air device."""
    device = AirDevice(serial_number=AIR_SERIAL_NUMBER, data=obs_air)
    assert device.model == "Air"
    assert device.serial_number == AIR_SERIAL_NUMBER
    assert device.hub_sn == HUB_SERIAL_NUMBER

    assert device.battery == 0 * UNIT_VOLTS
    device.parse_message(obs_air)
    assert device.air_temperature == 10.0 * UNIT_DEGREES_CELSIUS
    assert device.battery == 3.46 * UNIT_VOLTS
    assert device.last_report
    assert device.lightning_strike_average_distance == 0 * UNIT_KILOMETERS
    assert device.lightning_strike_count == 0
    assert device.relative_humidity == 45 * UNIT_PERCENT
    assert device.report_interval == 1 * UNIT_MINUTES
    assert device.station_pressure == 835.0 * UNIT_MILLIBARS

    obs_air.update({DATA_OBSERVATIONS: [[1493165835, 835.0, 10.0, 45, 0, 0, 3.45, 1]]})
    device.parse_message(obs_air)
    assert device.battery == 3.45 * UNIT_VOLTS


def test_sky_device(obs_sky: dict[str, Any]) -> None:
    """Test handling of a sky device."""
    device = SkyDevice(serial_number=SKY_SERIAL_NUMBER, data=obs_sky)
    assert device.model == "Sky"
    assert device.serial_number == SKY_SERIAL_NUMBER
    assert device.hub_sn == HUB_SERIAL_NUMBER

    assert device.battery == 0 * UNIT_VOLTS
    device.parse_message(obs_sky)
    assert device.battery == 3.12 * UNIT_VOLTS
    assert device.illuminance == 9000 * UNIT_LUX
    assert device.precipitation_type == PrecipitationType.NONE
    assert device.rain_amount_previous_minute == 0 * UNIT_MILLIMETERS_PER_MINUTE
    assert device.report_interval == 1 * UNIT_MINUTES
    assert device.solar_radiation == 130 * UNIT_IRRADIATION
    assert device.uv == 10
    assert device.wind_average == 4.6 * UNIT_METERS_PER_SECOND
    assert device.wind_direction == 187 * UNIT_DEGREES
    assert device.wind_direction_cardinal == "S"
    assert device.wind_gust == 7.4 * UNIT_METERS_PER_SECOND
    assert device.wind_lull == 2.6 * UNIT_METERS_PER_SECOND
    assert device.wind_sample_interval == 3 * UNIT_MINUTES


def test_tempest_device(
    device_status: dict[str, Any],
    evt_precip: dict[str, Any],
    evt_strike: dict[str, Any],
    rapid_wind: dict[str, Any],
    obs_st: dict[str, Any],
    obs_st_cold: dict[str, Any],
) -> None:
    """Test handling of a tempest device."""
    device = TempestDevice(serial_number=TEMPEST_SERIAL_NUMBER, data=device_status)
    assert device.model == "Tempest"
    assert device.serial_number == TEMPEST_SERIAL_NUMBER
    assert device.hub_sn == HUB_SERIAL_NUMBER

    def load_complete(event):
        assert event
        assert device.load_complete

    unsubscribe = device.on(EVENT_LOAD_COMPLETE, lambda event: load_complete(event))

    assert device.rssi == 0 * UNIT_DECIBELS
    device.parse_message(device_status)
    assert device.rssi == -17 * UNIT_DECIBELS
    assert device.hub_rssi == -87 * UNIT_DECIBELS
    assert device.sensor_status == []

    device_status.update({"rssi": -21})
    device.parse_message(device_status)
    assert device.rssi == -21 * UNIT_DECIBELS

    assert not device.last_rain_start_event
    device.parse_message(evt_precip)
    assert device.last_rain_start_event

    assert not device.last_lightning_strike_event
    device.parse_message(evt_strike)
    assert device.last_lightning_strike_event
    assert device.last_lightning_strike_event.distance == 27 * UNIT_KILOMETERS
    assert device.last_lightning_strike_event.energy == 3848

    assert not device.last_wind_event
    device.parse_message(rapid_wind)
    assert device.last_wind_event
    assert device.last_wind_event.speed == 2.3 * UNIT_METERS_PER_SECOND
    assert device.last_wind_event.direction == 128 * UNIT_DEGREES

    assert device.battery == 0 * UNIT_VOLTS
    device.parse_message(obs_st)
    assert device.air_temperature == 22.37 * UNIT_DEGREES_CELSIUS
    assert device.battery == 2.410 * UNIT_VOLTS
    assert device.illuminance == 328 * UNIT_LUX
    assert device.lightning_strike_average_distance == 0 * UNIT_KILOMETERS
    assert device.lightning_strike_count == 0
    assert device.precipitation_type == PrecipitationType.NONE
    assert device.rain_amount_previous_minute == 0 * UNIT_MILLIMETERS_PER_MINUTE
    assert device.relative_humidity == 50.26 * UNIT_PERCENT
    assert device.report_interval == 1 * UNIT_MINUTES
    assert device.solar_radiation == 3 * UNIT_IRRADIATION
    assert device.station_pressure == 1017.57 * UNIT_MILLIBARS
    assert device.uv == 0.03
    assert device.wind_average == 0.22 * UNIT_METERS_PER_SECOND
    assert device.wind_direction == 144 * UNIT_DEGREES
    assert device.wind_direction_cardinal == "SE"
    assert device.wind_gust == 0.27 * UNIT_METERS_PER_SECOND
    assert device.wind_lull == 0.18 * UNIT_METERS_PER_SECOND
    assert device.wind_sample_interval == 6 * UNIT_MINUTES
    assert round(device.air_density, 5) == 1.19959 * UNIT_KILOGRAMS_PER_CUBIC_METER
    assert round(device.delta_t, 5) == 6.59114 * units.delta_degC
    assert round(device.dew_point_temperature, 5) == 11.52825 * UNIT_DEGREES_CELSIUS
    assert device.feels_like_temperature == 22.37 * UNIT_DEGREES_CELSIUS
    assert device.heat_index is None
    assert (
        round(device.calculate_sea_level_pressure(units.Quantity(1000, units.m)), 5)
        == 1140.84234 * UNIT_MILLIBARS
    )
    assert round(device.vapor_pressure, 5) == 1359.55045 * UNIT_MILLIBARS
    assert round(device.wet_bulb_temperature, 5) == 15.77886 * UNIT_DEGREES_CELSIUS
    assert device.wind_chill_temperature is None

    unsubscribe()


def test_tempest_device_cold_weather(
    obs_st_cold: dict[str, Any],
) -> None:
    """Test handling of a tempest device with cold weather."""
    device = TempestDevice(serial_number=TEMPEST_SERIAL_NUMBER, data=obs_st_cold)
    device.parse_message(obs_st_cold)
    assert device.air_temperature == 0.37 * UNIT_DEGREES_CELSIUS
    assert device.heat_index is None
    assert round(device.wind_chill_temperature, 5) == -1.33298 * UNIT_DEGREES_CELSIUS
    assert round(device.feels_like_temperature, 5) == -1.33298 * UNIT_DEGREES_CELSIUS


def test_tempest_device_hot_weather(
    obs_st_hot: dict[str, Any],
) -> None:
    """Test handling of a tempest device with hot weather."""
    device = TempestDevice(serial_number=TEMPEST_SERIAL_NUMBER, data=obs_st_hot)
    device.parse_message(obs_st_hot)
    assert device.air_temperature == 30.37 * UNIT_DEGREES_CELSIUS
    assert round(device.heat_index, 5) == 31.65311 * UNIT_DEGREES_CELSIUS
    assert device.wind_chill_temperature is None
    assert round(device.feels_like_temperature, 5) == 31.65311 * UNIT_DEGREES_CELSIUS


def test_alternate_parse_message_paths(caplog: LogCaptureFixture):
    device = HubDevice(serial_number=HUB_SERIAL_NUMBER)
    device.parse_message({"type": "no_handler"})
    assert "Unhandled no_handler message" in caplog.text
