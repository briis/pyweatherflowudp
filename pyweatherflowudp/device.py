"""WeatherFlow devices."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Callable, final

from pint import Quantity

from .calc import wind_chill
from .const import (
    EVENT_OBSERVATION_AIR,
    EVENT_OBSERVATION_SKY,
    EVENT_OBSERVATION_TEMPEST,
    EVENT_RAIN_START,
    EVENT_RAPID_WIND,
    EVENT_STATUS_DEVICE,
    EVENT_STATUS_HUB,
    EVENT_STRIKE,
    UNIT_DECIBELS,
    UNIT_SECONDS,
)
from .event import CustomEvent, LightningStrikeEvent, RainStartEvent, WindEvent
from .helpers import truebool, utc_timestamp_from_epoch
from .mixins import AirSensorMixin, BaseSensorMixin, EventMixin, SkySensorMixin

DATA_DEBUG = "debug"
DATA_EVENT = "evt"
DATA_FIRMWARE_REVISION = "firmware_revision"
DATA_HUB_RSSI = "hub_rssi"
DATA_HUB_SN = "hub_sn"
DATA_OBSERVATION = "ob"
DATA_OBSERVATIONS = "obs"
DATA_RADIO_STATS = "radio_stats"
DATA_RESET_FLAGS = "reset_flags"
DATA_RSSI = "rssi"
DATA_SENSOR_STATUS = "sensor_status"
DATA_SEQ = "seq"
DATA_TIMESTAMP = "timestamp"
DATA_TYPE = "type"
DATA_UPTIME = "uptime"
DATA_VOLTAGE = "voltage"

EVENT_LOAD_COMPLETE = "load_complete"
EVENT_OBSERVATION = "observation"
EVENT_STATUS_UPDATE = "status_update"

RESET_FLAGS = {
    "BOR": "Brownout reset",
    "PIN": "PIN reset",
    "POR": "Power reset",
    "SFT": "Software reset",
    "WDG": "Watchdog reset",
    "WWD": "Window watchdog reset",
    "LPW": "Low-power reset",
    "HRDFLT": "Hard fault detected",
}

RAIN_START_EVENT_TIMESTAMP = 0

STRIKE_EVENT_TIMESTAMP = 0
STRIKE_EVENT_DISTANCE = 1
STRIKE_EVENT_ENERGY = 2

WIND_OBSERVATION_TIMESTAMP = 0
WIND_OBSERVATION_SPEED = 1
WIND_OBSERVATION_DIRECTION = 2

_LOGGER = logging.getLogger(__name__)


class WeatherFlowDevice(EventMixin):
    """Generic WeatherFlow device."""

    _attr_model = "Unknown"

    def __init__(self, serial_number: str, data: dict[str, Any] | None = None) -> None:
        """Initialize a WeatherFlow device."""
        # pylint: disable=unused-argument
        self._serial_number = serial_number
        self._firmware_revision: str | None = None
        self._rssi: int = 0
        self._timestamp: int | None = None
        self._uptime: int = 0
        self._initial_status: bool = False

        self._listeners: dict[str, list[Callable]] = {}
        self._parse_message_map: dict[str, Callable | tuple[Callable, str]] = {}

    @property
    def firmware_revision(self) -> str:
        """Return firmware revision."""
        return str(self._firmware_revision)

    @property
    def load_complete(self) -> bool:
        """Return `True` if the device has been completely loaded."""
        return self._initial_status

    @property
    def model(self) -> str:
        """Return the model."""
        return self._attr_model

    @property
    def rssi(self) -> Quantity[int]:
        """Return the rssi."""
        return self._rssi * UNIT_DECIBELS

    @property
    def serial_number(self) -> str:
        """Return the serial number."""
        return self._serial_number

    @property
    def timestamp(self) -> datetime | None:
        """Return the timestamp in UTC."""
        return utc_timestamp_from_epoch(self._timestamp)

    @property
    def up_since(self) -> datetime | None:
        """Return the device's up since timestamp in UTC."""
        return (
            None
            if self._timestamp is None
            else utc_timestamp_from_epoch(self._timestamp - self._uptime)
        )

    @property
    def uptime(self) -> Quantity[int]:
        """Return the uptime in seconds."""
        return self._uptime * UNIT_SECONDS

    def register_parse_handlers(
        self, message_handlers: dict[str, Callable | tuple[Callable, str]]
    ) -> None:
        """Register or replace a parse handler."""
        for message_type, handler in message_handlers.items():
            self._parse_message_map[message_type] = handler

    @final
    def parse_message(self, data: dict[str, Any]) -> None:
        """Parse a device message."""
        if handler := self._parse_message_map.get(
            message_type := data.get(DATA_TYPE, "")
        ):
            if isinstance(handler, tuple):
                handler, field = handler
                data = data.get(field, {})
            handler(data)
        else:
            _LOGGER.warning("Unhandled %s message: %s", message_type, data)


class HubDevice(WeatherFlowDevice):
    """Represents a WeatherFlow Hub."""

    _attr_model = "Hub"

    def __init__(self, serial_number: str, data: dict[str, Any] | None = None) -> None:
        """Initialize a WeatherFlow hub device."""
        super().__init__(serial_number=serial_number, data=data)

        self._reset_flags: str = ""
        self._seq: int = 0
        self._radio_stats: list[int] = []

        self.register_parse_handlers({EVENT_STATUS_HUB: self.parse_hub_status})

    def __repr__(self) -> str:  # pragma: no cover
        """Return repr(self)."""
        return f"{self.model}<serial_number={self.serial_number}>"

    @property
    def reset_flags(self) -> list[str] | None:
        """Return the list of reset flags."""
        return [
            RESET_FLAGS[flag]
            for flag in self._reset_flags.split(",")
            if flag in RESET_FLAGS
        ]

    def parse_hub_status(self, data: dict[str, Any]) -> None:
        """Parse hub status."""
        self._firmware_revision = data.get(DATA_FIRMWARE_REVISION)
        self._uptime = data.get(DATA_UPTIME, 0)
        self._rssi = data.get(DATA_RSSI, 0)
        self._timestamp = data.get(DATA_TIMESTAMP)
        self._reset_flags = data.get(DATA_RESET_FLAGS, "")
        self._seq = data.get(DATA_SEQ, 0)
        self._radio_stats = data.get(DATA_RADIO_STATS, [])

        assert self._timestamp

        if not self._initial_status:
            self._initial_status = True
            self.emit(
                EVENT_LOAD_COMPLETE,
                CustomEvent(self._timestamp, EVENT_LOAD_COMPLETE),
            )

        self.emit(
            EVENT_STATUS_UPDATE, CustomEvent(self._timestamp, EVENT_STATUS_UPDATE)
        )


class WeatherFlowSensorDevice(BaseSensorMixin, WeatherFlowDevice):
    """Represents a WeatherFlow sensor device."""

    _evt_observation: str = ""

    OBSERVATION_VALUES_MAP: dict[int, str] = {}

    SENSOR_STATUS_MASK = {
        0b000000001: "Lightning Failed",
        0b000000010: "Lightning Noise",
        0b000000100: "Lightning Disturber",
        0b000001000: "Pressure Failed",
        0b000010000: "Temperature Failed",
        0b000100000: "Relative Humidity Failed",
        0b001000000: "Wind Failed",
        0b010000000: "Precipitation Failed",
        0b100000000: "Light/UV Failed",
        0x00008000: "Power Booster Depleted",
        0x00010000: "Power Booster Shore Power",
    }

    def __init__(self, serial_number: str, data: dict[str, Any] | None = None) -> None:
        """Initialize a WeatherFlow device."""
        super().__init__(serial_number=serial_number, data=data)

        self._hub_sn: str | None = data.get(DATA_HUB_SN) if data is not None else None
        self._voltage: float = 0
        self._hub_rssi: int = 0
        self._sensor_status: int = 0
        self._debug: bool = False
        self._initial_observation: bool = False

        self.register_parse_handlers(
            {
                self._evt_observation: (self.parse_observation, DATA_OBSERVATIONS),
                EVENT_STATUS_DEVICE: self.parse_device_status,
            }
        )

    def __repr__(self) -> str:  # pragma: no cover
        """Return repr(self)."""
        return f"{self.model}<serial_number={self.serial_number}, hub={self.hub_sn}>"

    @property
    def hub_rssi(self) -> Quantity[int]:
        """Return the hub rssi."""
        return self._hub_rssi * UNIT_DECIBELS

    @property
    def hub_sn(self) -> str | None:
        """Return the hub serial number."""
        return self._hub_sn

    @property
    def load_complete(self) -> bool:
        """Return `True` if the device has been completely loaded."""
        return self._initial_status and self._initial_observation

    @property
    def sensor_status(self) -> list[str]:
        """Return the sensor status."""
        return (
            []
            if self._sensor_status is None
            else [
                status
                for mask in self.SENSOR_STATUS_MASK
                if (status := self.SENSOR_STATUS_MASK.get(mask & self._sensor_status))
                is not None
            ]
        )

    def parse_device_status(self, data: dict[str, Any]) -> None:
        """Parse the device status."""
        self._timestamp = data.get(DATA_TIMESTAMP)
        self._uptime = data.get(DATA_UPTIME, 0)
        self._voltage = data.get(DATA_VOLTAGE, 0)
        self._firmware_revision = data.get(DATA_FIRMWARE_REVISION)
        self._rssi = data.get(DATA_RSSI, 0)
        self._hub_rssi = data.get(DATA_HUB_RSSI, 0)
        self._sensor_status = data.get(DATA_SENSOR_STATUS, 0)
        self._debug = truebool(data.get(DATA_DEBUG))

        if not self._initial_status:
            self._initial_status = True
            self._send_load_complete_event()

        assert self._timestamp
        self.emit(
            EVENT_STATUS_UPDATE, CustomEvent(self._timestamp, EVENT_STATUS_UPDATE)
        )

    def parse_observation(self, data: list[list]) -> None:
        """Parse observation data."""
        for observation in data:
            for idx, field in self.OBSERVATION_VALUES_MAP.items():
                setattr(self, field, observation[idx])

        if not self._initial_observation:
            self._initial_observation = True
            self._send_load_complete_event()

        assert self._last_report
        self.emit(EVENT_OBSERVATION, CustomEvent(self._last_report, EVENT_OBSERVATION))

    def _send_load_complete_event(self) -> None:
        if self._initial_status and self._initial_observation:
            assert self._last_report
            assert self._timestamp
            self.emit(
                EVENT_LOAD_COMPLETE,
                CustomEvent(
                    max(self._timestamp, self._last_report), EVENT_LOAD_COMPLETE
                ),
            )


class AirSensorType(AirSensorMixin, WeatherFlowSensorDevice):
    """Air sensor type class."""

    def __init__(self, serial_number: str, data: dict[str, Any] | None = None) -> None:
        """Initialize a WeatherFlow air sensor device."""
        super().__init__(serial_number=serial_number, data=data)

        self.register_parse_handlers(
            {EVENT_STRIKE: (self.parse_strike_event, DATA_EVENT)}
        )

    def parse_strike_event(self, data: list) -> None:
        """Parse strike event data."""
        if (report_timestamp := data[STRIKE_EVENT_TIMESTAMP]) < (
            0
            if self._last_lightning_strike_event is None
            else self._last_lightning_strike_event.epoch
        ):  # pragma: no cover
            _LOGGER.warning("Received an old strike event: %s", data)
            return

        self._last_lightning_strike_event = LightningStrikeEvent(
            report_timestamp, data[STRIKE_EVENT_DISTANCE], data[STRIKE_EVENT_ENERGY]
        )

        self.emit(EVENT_STRIKE, self._last_lightning_strike_event)


class SkySensorType(SkySensorMixin, WeatherFlowSensorDevice):
    """Sky sensor type class."""

    def __init__(self, serial_number: str, data: dict[str, Any] | None = None) -> None:
        """Initialize a WeatherFlow device."""
        super().__init__(serial_number=serial_number, data=data)

        self.register_parse_handlers(
            {
                EVENT_RAIN_START: (self.parse_rain_start_event, DATA_EVENT),
                EVENT_RAPID_WIND: (self.parse_wind_event, DATA_OBSERVATION),
            }
        )

    def parse_rain_start_event(self, data: list) -> None:
        """Parse rain start event data."""
        if (report_timestamp := data[RAIN_START_EVENT_TIMESTAMP]) < (
            0
            if self._last_rain_start_event is None
            else self._last_rain_start_event.epoch
        ):  # pragma: no cover
            _LOGGER.warning("Received an old rain start event: %s", data)
            return

        self._last_rain_start_event = RainStartEvent(report_timestamp)

        self.emit(EVENT_RAIN_START, self._last_rain_start_event)

    def parse_wind_event(self, data: list) -> None:
        """Parse wind event data."""
        if (report_timestamp := data[WIND_OBSERVATION_TIMESTAMP]) < (
            0 if self._last_wind_event is None else self._last_wind_event.epoch
        ):  # pragma: no cover
            _LOGGER.warning("Received an old wind report: %s", data)
            return

        self._last_wind_event = WindEvent(
            report_timestamp,
            data[WIND_OBSERVATION_SPEED],
            data[WIND_OBSERVATION_DIRECTION],
        )

        self.emit(EVENT_RAPID_WIND, self._last_wind_event)


class AirDevice(AirSensorType):
    """Represents a WeatherFlow Air device."""

    _attr_model = "Air"
    _evt_observation = EVENT_OBSERVATION_AIR

    OBSERVATION_VALUES_MAP = {
        0: "_last_report",
        1: "_station_pressure",
        2: "_air_temperature",
        3: "_relative_humidity",
        4: "_lightning_strike_count",
        5: "_lightning_strike_average_distance",
        6: "_battery",
        7: "_report_interval",
    }


class SkyDevice(SkySensorType):
    """Represents a WeatherFlow Sky device."""

    _attr_model = "Sky"
    _evt_observation = EVENT_OBSERVATION_SKY

    OBSERVATION_VALUES_MAP = {
        0: "_last_report",
        1: "_illuminance",
        2: "_uv",
        3: "_rain_accumulation_previous_minute",
        4: "_wind_lull",
        5: "_wind_average",
        6: "_wind_gust",
        7: "_wind_direction",
        8: "_battery",
        9: "_report_interval",
        10: "_solar_radiation",
        12: "_precipitation_type",
        13: "_wind_sample_interval",
    }


class TempestDevice(AirSensorType, SkySensorType):
    """Represents a WeatherFlow Tempest device."""

    _attr_model = "Tempest"
    _evt_observation = EVENT_OBSERVATION_TEMPEST

    OBSERVATION_VALUES_MAP = {
        0: "_last_report",
        1: "_wind_lull",
        2: "_wind_average",
        3: "_wind_gust",
        4: "_wind_direction",
        5: "_wind_sample_interval",
        6: "_station_pressure",
        7: "_air_temperature",
        8: "_relative_humidity",
        9: "_illuminance",
        10: "_uv",
        11: "_solar_radiation",
        12: "_rain_accumulation_previous_minute",
        13: "_precipitation_type",
        14: "_lightning_strike_average_distance",
        15: "_lightning_strike_count",
        16: "_battery",
        17: "_report_interval",
    }

    # Derived metrics

    @property
    def feels_like_temperature(self) -> Quantity[float] | None:
        """Return the feels like temperature in degrees Celsius (°C)."""
        if self.heat_index is not None:
            return self.heat_index
        if self.wind_chill_temperature is not None:
            return self.wind_chill_temperature
        return self.air_temperature

    @property
    def wind_chill_temperature(self) -> Quantity[float] | None:
        """Return the calculated wind chill temperature in degrees Celsius (°C)."""
        if None in (self.air_temperature, self.wind_speed):
            return None
        return wind_chill(self.air_temperature, self.wind_speed)


SERIAL_MAP = {"HB": HubDevice, "AR": AirDevice, "SK": SkyDevice, "ST": TempestDevice}


def determine_device(serial_number: str) -> type[WeatherFlowDevice]:
    """Return the type of WeatherFlow device from a serial number."""
    return SERIAL_MAP.get(serial_number[:2], WeatherFlowDevice)
