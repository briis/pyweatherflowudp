"""Tests for pysecspy_server."""

import aiohttp
import pytest

from pyweatherflowudp.client import WeatherFlowListner


@pytest.mark.asyncio
async def test_server_creation():
    """Test we can create the object."""

    wfl = WeatherFlowListner("Test Server", "127.0.0.1", 50222)
    assert wfl
