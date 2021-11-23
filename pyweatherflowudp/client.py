"""WeatherFlow client."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from .aioudp import LocalEndpoint, open_local_endpoint
from .const import DEFAULT_HOST, DEFAULT_PORT
from .device import WeatherFlowDevice, detmine_device
from .mixins import EventMixin

DATA_HUB_SN = "hub_sn"
DATA_SERIAL_NUMBER = "serial_number"

EVENT_DEVICE_DISCOVERED = "device_discovered"

_LOGGER = logging.getLogger(__name__)


class WeatherFlowListener(EventMixin):
    """WeatherFlow listener."""

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
    ) -> None:
        """Initialize a WeatherFlow listener."""
        self._host = host
        self._port = port
        self._devices: dict[str, WeatherFlowDevice] = {}
        self._udp_task: asyncio.Task | None = None
        self._udp_connection: LocalEndpoint | None = None

    @property
    def is_listening(self) -> bool:
        """Return `True` if the client is listening for messages."""
        return self._udp_task is not None

    async def start_listening(self) -> None:
        """Connect the UDP socket and start listening for messages."""
        if self._udp_task is not None:
            return

        self._udp_task = asyncio.ensure_future(self._setup_socketreader())
        _LOGGER.debug("Started listening")

    async def stop_listening(self) -> None:
        """Disconnect the socket."""
        if self._udp_task is None:
            return

        if self._udp_connection is not None and not self._udp_connection.closed:
            self._udp_connection.close()

        self._udp_task.cancel()
        try:
            await self._udp_task
        except asyncio.CancelledError:
            pass
        finally:
            self._udp_task = None
            _LOGGER.debug("Stopped listening")

    async def _setup_socketreader(self) -> None:
        """Setup the UDP Socket Listener."""
        self._udp_connection = await open_local_endpoint(
            host=self._host, port=self._port
        )
        assert self._udp_connection

        while not self._udp_connection.closed:
            data, (host, port) = await self._udp_connection.receive()
            _LOGGER.debug("Received message from %s:%s - %s", host, port, data)
            self._process_message(data)

    def _process_message(self, data: bytes) -> None:
        """Process a UDP message."""
        json_data: dict[str, Any] = json.loads(data)

        if (serial_number := json_data[DATA_SERIAL_NUMBER]) not in self._devices:
            self._devices[serial_number] = detmine_device(serial_number)(
                serial_number=serial_number, data=json_data
            )
            self.emit(EVENT_DEVICE_DISCOVERED, self._devices[serial_number])
        self._devices[serial_number].parse_message(json_data)

    async def __aenter__(self) -> WeatherFlowListener:
        """Connect the UDP socket and start listening for messages."""
        await self.start_listening()
        return self

    async def __aexit__(self, *exctype: Any) -> None:
        """Disconnect the socket."""
        await self.stop_listening()
