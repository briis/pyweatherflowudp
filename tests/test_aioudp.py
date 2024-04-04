"""Test UDP socket connection."""

import asyncio

import pytest

from pyweatherflowudp.aioudp import open_local_endpoint, open_remote_endpoint

pytestmark = pytest.mark.asyncio


async def test_standard_behavior() -> None:
    """Test standard behavior."""
    local = await open_local_endpoint()
    remote = await open_remote_endpoint(*local.address)

    remote.send(b"Hey Hey")
    data, address = await local.receive()

    assert data == b"Hey Hey"
    assert address == remote.address

    local.send(b"My My", address)
    data, address = await remote.receive()
    assert data == b"My My"
    assert address == (remote.address[0], local.address[1])

    local.abort()
    assert local.closed

    with pytest.warns(UserWarning):
        await asyncio.sleep(1e-3)
        remote.send(b"U there?")
        await asyncio.sleep(1e-3)

    remote.abort()
    assert remote.closed


async def test_closed_endpoint() -> None:
    """Test closed endpoint."""
    local = await open_local_endpoint()
    future = asyncio.ensure_future(local.receive())
    local.abort()
    assert local.closed

    with pytest.raises(IOError):
        await future

    with pytest.raises(IOError):
        await local.receive()

    with pytest.raises(IOError):
        await local.send(b"test", ("localhost", 8888))

    with pytest.raises(IOError):
        local.abort()


async def test_queue_size() -> None:
    """Test queue size."""
    local = await open_local_endpoint(queue_size=1)
    remote = await open_remote_endpoint(*local.address)

    remote.send(b"1")
    remote.send(b"2")
    with pytest.warns(UserWarning):
        await asyncio.sleep(1e-3)
        assert await local.receive() == (b"1", remote.address)
    remote.send(b"3")
    assert await local.receive() == (b"3", remote.address)

    remote.send(b"4")
    await asyncio.sleep(1e-3)
    local.abort()
    assert local.closed
    assert await local.receive() == (b"4", remote.address)

    remote.abort()
    assert remote.closed


async def test_flow_control() -> None:
    """Test flow control."""
    m = n = 1024
    remote = await open_remote_endpoint("8.8.8.8", 12345)

    for _ in range(m):
        remote.send(b"a" * n)

    await remote.drain()

    for _ in range(m):
        remote.send(b"a" * n)

    remote.abort()
    await remote.drain()
