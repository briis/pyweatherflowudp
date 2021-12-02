"""Provide common pytest fixtures."""
import json
from typing import Any

import pytest

from pyweatherflowudp.aioudp import (
    RemoteEndpoint,
    open_local_endpoint,
    open_remote_endpoint,
)
from pyweatherflowudp.client import WeatherFlowListener

from . import load_fixture


@pytest.fixture(name="device_status")
def device_status_fixture() -> dict[str, Any]:
    """Load the device_status fixture data."""
    return json.loads(load_fixture("device_status.json"))


@pytest.fixture(name="evt_precip")
def evt_precip_fixture() -> dict[str, Any]:
    """Load the evt_precip fixture data."""
    return json.loads(load_fixture("evt_precip.json"))


@pytest.fixture(name="evt_strike")
def evt_strike_fixture() -> dict[str, Any]:
    """Load the evt_strike fixture data."""
    return json.loads(load_fixture("evt_strike.json"))


@pytest.fixture(name="hub_status")
def hub_status_fixture() -> dict[str, Any]:
    """Load the hub_status fixture data."""
    return json.loads(load_fixture("hub_status.json"))


@pytest.fixture(name="obs_air")
def obs_air_fixture() -> dict[str, Any]:
    """Load the obs_air fixture data."""
    return json.loads(load_fixture("obs_air.json"))


@pytest.fixture(name="obs_sky")
def obs_sky_fixture() -> dict[str, Any]:
    """Load the obs_sky fixture data."""
    return json.loads(load_fixture("obs_sky.json"))


@pytest.fixture(name="obs_st")
def obs_st_fixture() -> dict[str, Any]:
    """Load the obs_st fixture data."""
    return json.loads(load_fixture("obs_st.json"))


@pytest.fixture(name="obs_st_cold")
def obs_st_cold_fixture() -> dict[str, Any]:
    """Load the obs_st_cold fixture data."""
    return json.loads(load_fixture("obs_st_cold.json"))


@pytest.fixture(name="obs_st_hot")
def obs_st_hot_fixture() -> dict[str, Any]:
    """Load the obs_st_hot fixture data."""
    return json.loads(load_fixture("obs_st_hot.json"))


@pytest.fixture(name="rapid_wind")
def rapid_wind_fixture() -> dict[str, Any]:
    """Load the rapid_wind fixture data."""
    return json.loads(load_fixture("rapid_wind.json"))


@pytest.fixture(name="local_address")
async def local_address_fixture() -> tuple[str, int]:
    """Get a local endpoint address."""
    local = await open_local_endpoint()
    local.abort()
    assert local.closed
    assert isinstance(local.address, tuple)
    return local.address


@pytest.fixture(name="remote_endpoint")
async def remote_endpoint_fixture(local_address: tuple[str, int]) -> RemoteEndpoint:
    """Create a local endpoint."""
    return await open_remote_endpoint(*local_address)


@pytest.fixture(name="listener")
def listener_fixture(local_address: tuple[str, int]) -> WeatherFlowListener:
    """Return a WeatherFlow listener."""
    listener = WeatherFlowListener(*local_address)
    return listener
