"""Test devices."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

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

    assert device.rssi == 0
    device.parse_message(hub_status)
    assert device.rssi == -62
    assert device.firmware_revision == "35"
    assert device.timestamp == datetime.fromtimestamp(1495724691, timezone.utc)
    assert device.uptime == 1670133
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

    assert device.battery == 0
    device.parse_message(obs_air)
    assert device.air_temperature == 10.0
    assert device.battery == 3.46
    assert device.last_report
    assert device.lightning_strike_average_distance == 0
    assert device.lightning_strike_count == 0
    assert device.relative_humidity == 45
    assert device.report_interval == 1
    assert device.station_pressure == 835.0

    obs_air.update({DATA_OBSERVATIONS: [[1493165835, 835.0, 10.0, 45, 0, 0, 3.45, 1]]})
    device.parse_message(obs_air)
    assert device.battery == 3.45


def test_sky_device(obs_sky: dict[str, Any]) -> None:
    """Test handling of a sky device."""
    device = SkyDevice(serial_number=SKY_SERIAL_NUMBER, data=obs_sky)
    assert device.model == "Sky"
    assert device.serial_number == SKY_SERIAL_NUMBER
    assert device.hub_sn == HUB_SERIAL_NUMBER

    assert device.battery == 0
    device.parse_message(obs_sky)
    assert device.battery == 3.12
    assert device.illuminance == 9000
    assert device.precipitation_type == PrecipitationType.NONE
    assert device.rain_amount_previous_minute == 0
    assert device.report_interval == 1
    assert device.solar_radiation == 130
    assert device.uv == 10
    assert device.wind_average == 4.6
    assert device.wind_direction == 187
    assert device.wind_gust == 7.4
    assert device.wind_lull == 2.6
    assert device.wind_sample_interval == 3


def test_tempest_device(
    device_status: dict[str, Any],
    evt_precip: dict[str, Any],
    evt_strike: dict[str, Any],
    rapid_wind: dict[str, Any],
    obs_st: dict[str, Any],
) -> None:
    """Test handling of a tempest device."""
    device = TempestDevice(serial_number=TEMPEST_SERIAL_NUMBER, data=device_status)
    assert device.model == "Tempest"
    assert device.serial_number == TEMPEST_SERIAL_NUMBER
    assert device.hub_sn == HUB_SERIAL_NUMBER

    def load_complete(event):
        assert event

    unsubscribe = device.on(EVENT_LOAD_COMPLETE, lambda event: load_complete(event))

    assert device.rssi == 0
    device.parse_message(device_status)
    assert device.rssi == -17
    assert device.sensor_status == []

    device_status.update({"rssi": -21})
    device.parse_message(device_status)
    assert device.rssi == -21

    assert not device.last_rain_start_event
    device.parse_message(evt_precip)
    assert device.last_rain_start_event

    assert not device.last_lightning_strike_event
    device.parse_message(evt_strike)
    assert device.last_lightning_strike_event
    assert device.last_lightning_strike_event.distance == 27
    assert device.last_lightning_strike_event.energy == 3848

    assert not device.last_wind_event
    device.parse_message(rapid_wind)
    assert device.last_wind_event
    assert device.last_wind_event.speed == 2.3
    assert device.last_wind_event.direction == 128

    assert device.battery == 0
    device.parse_message(obs_st)
    assert device.air_temperature == 22.37
    assert device.battery == 2.410
    assert device.illuminance == 328
    assert device.lightning_strike_average_distance == 0
    assert device.lightning_strike_count == 0
    assert device.precipitation_type == PrecipitationType.NONE
    assert device.rain_amount_previous_minute == 0
    assert device.relative_humidity == 50.26
    assert device.report_interval == 1
    assert device.solar_radiation == 3
    assert device.station_pressure == 1017.57
    assert device.uv == 0.03
    assert device.wind_average == 0.22
    assert device.wind_direction == 144
    assert device.wind_gust == 0.27
    assert device.wind_lull == 0.18
    assert device.wind_sample_interval == 6

    unsubscribe()


def test_alternate_parse_message_paths(caplog):
    device = HubDevice(serial_number=HUB_SERIAL_NUMBER)
    device.parse_message({"type": "no_handler"})
    assert "Unhandled no_handler message" in caplog.text
