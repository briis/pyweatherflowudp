"""Tests for pysecspy_server."""

import aiohttp
import pytest

from pysecspy.secspy_server import SecSpyServer


@pytest.mark.asyncio
async def test_server_creation():
    """Test we can create the object."""

    sec = SecSpyServer(aiohttp.ClientSession(), "127.0.0.1", 0, "username", "password")
    assert sec
