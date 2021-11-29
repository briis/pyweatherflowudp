"""Test client listener behavior."""
from __future__ import annotations

import asyncio
import json
from typing import Any
from unittest.mock import patch

import pytest
from _pytest.logging import LogCaptureFixture

from pyweatherflowudp.aioudp import RemoteEndpoint
from pyweatherflowudp.client import WeatherFlowListener
from pyweatherflowudp.errors import AddressInUseError

pytestmark = pytest.mark.asyncio


async def test_listen_and_stop(listener: WeatherFlowListener) -> None:
    """Test listen and stop."""
    async with listener:
        assert listener.is_listening
        await asyncio.sleep(0.1)

    assert not listener.is_listening


async def test_repetitive_listen_and_stop(listener: WeatherFlowListener) -> None:
    """Test repetitive listen and stop."""
    assert not listener.is_listening

    repeat = 2

    for _ in range(repeat):
        await listener.start_listening()
        assert listener.is_listening
    for _ in range(repeat):
        await listener.stop_listening()
        assert not listener.is_listening


async def test_process_message(
    listener: WeatherFlowListener,
    remote_endpoint: RemoteEndpoint,
    device_status: dict[str, Any],
) -> None:
    """Test processing a received message."""
    await listener.start_listening()
    await asyncio.sleep(0.1)
    remote_endpoint.send(bytes(json.dumps(device_status), "UTF-8"))
    await asyncio.sleep(0.1)
    await listener.stop_listening()


async def test_listener_connection_errors(listener: WeatherFlowListener) -> None:
    """Test listener connection errors."""
    with patch(
        "asyncio.base_events.BaseEventLoop.create_datagram_endpoint",
        side_effect=OSError(48, "Address already in use"),
    ), pytest.raises(AddressInUseError):
        await listener.start_listening()


async def test_invalid_messages(
    listener: WeatherFlowListener,
    remote_endpoint: RemoteEndpoint,
    caplog: LogCaptureFixture,
) -> None:
    """Test invalid messages received by the listener."""
    await listener.start_listening()
    await asyncio.sleep(0.1)

    for invalid_message in [json.dumps({}), "blahblahblah"]:
        remote_endpoint.send(bytes(invalid_message, "UTF-8"))
        await asyncio.sleep(0.1)
        assert "Received unknown message" in caplog.text

    await listener.stop_listening()
    assert not listener.is_listening
