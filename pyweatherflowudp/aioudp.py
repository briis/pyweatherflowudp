"""Provide high-level UDP endpoints for asyncio.

Copied/modified from https://gist.github.com/vxgmichel/e47bff34b68adb3cf6bd4845c4bed448
"""
from __future__ import annotations

__all__ = ["open_local_endpoint", "open_remote_endpoint"]

import asyncio
import warnings
from typing import Any

# pylint: disable=protected-access

# Datagram protocol


class DatagramEndpointProtocol(asyncio.DatagramProtocol):
    """Datagram protocol for the endpoint high-level interface."""

    def __init__(self, endpoint: Endpoint) -> None:
        self._endpoint = endpoint

    # Protocol methods

    def connection_made(self, transport: Any) -> None:
        self._endpoint._transport = transport

    def connection_lost(self, exc: Any) -> None:
        assert exc is None
        if self._endpoint._write_ready_future is not None:  # pragma: no cover
            self._endpoint._write_ready_future.set_result(None)
        self._endpoint.close()

    # Datagram protocol methods

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        self._endpoint.feed_datagram(data, addr)

    def error_received(self, exc: Any) -> None:
        msg = "Endpoint received an error: {!r}"
        warnings.warn(msg.format(exc))

    # Workflow control

    def pause_writing(self) -> None:  # pragma: no cover
        assert self._endpoint._write_ready_future is None
        assert self._endpoint._transport._loop
        loop = self._endpoint._transport._loop
        self._endpoint._write_ready_future = loop.create_future()

    def resume_writing(self) -> None:  # pragma: no cover
        assert self._endpoint._write_ready_future is not None
        self._endpoint._write_ready_future.set_result(None)
        self._endpoint._write_ready_future = None


# Enpoint classes


class Endpoint:
    """High-level interface for UDP enpoints.

    Can either be local or remote.
    It is initialized with an optional queue size for the incoming datagrams.
    """

    def __init__(self, queue_size: int | None = None) -> None:
        if queue_size is None:
            queue_size = 0
        self._queue: asyncio.Queue = asyncio.Queue(queue_size)
        self._closed = False
        self._transport: Any = None
        self._write_ready_future: asyncio.Future | None = None

    # Protocol callbacks

    def feed_datagram(self, data: bytes | None, addr: tuple[str, int] | None) -> None:
        """Feed a datagram."""
        try:
            self._queue.put_nowait((data, addr))
        except asyncio.QueueFull:
            warnings.warn("Endpoint queue is full")

    def close(self) -> None:
        """Close the endpoint."""
        # Manage flag
        if self._closed:
            return
        self._closed = True
        # Wake up
        if self._queue.empty():
            self.feed_datagram(None, None)
        # Close transport
        if self._transport:
            self._transport.close()

    # User methods

    def send(self, data: bytes, addr: tuple[str, int] | None) -> None:
        """Send a datagram to the given address."""
        if self._closed:
            raise IOError("Enpoint is closed")
        self._transport.sendto(data, addr)

    async def receive(self) -> tuple[bytes, tuple[str, int]]:
        """Wait for an incoming datagram and return it with the corresponding address.

        This method is a coroutine.
        """
        if self._queue.empty() and self._closed:
            raise IOError("Enpoint is closed")
        data, addr = await self._queue.get()
        if data is None:
            raise IOError("Enpoint is closed")
        return data, addr

    def abort(self) -> None:
        """Close the transport immediately."""
        if self._closed:
            raise IOError("Enpoint is closed")
        self._transport.abort()
        self.close()

    async def drain(self) -> None:
        """Drain the transport buffer below the low-water mark."""
        if self._write_ready_future is not None:  # pragma: no cover
            await self._write_ready_future

    # Properties

    @property
    def address(self) -> Any:
        """Endpoint address as a (host, port) tuple."""
        return self._transport.get_extra_info("socket").getsockname()

    @property
    def closed(self) -> bool:
        """Indicate whether the endpoint is closed or not."""
        return self._closed


class LocalEndpoint(Endpoint):
    """High-level interface for UDP local enpoints.

    It is initialized with an optional queue size for the incoming datagrams.
    """


class RemoteEndpoint(Endpoint):
    """High-level interface for UDP remote enpoints.

    It is initialized with an optional queue size for the incoming datagrams.
    """

    def send(self, data: bytes, addr: tuple[str, int] | None = None) -> None:
        """Send a datagram to the remote host."""
        super().send(data, None)


# High-level coroutines


async def open_datagram_endpoint(
    host: str,
    port: int,
    *,
    endpoint_factory: Any = Endpoint,
    remote: bool = False,
    **kwargs: Any
) -> Any:
    """Open and return a datagram endpoint.

    The default endpoint factory is the Endpoint class.
    The endpoint can be made local or remote using the remote argument.
    Extra keyword arguments are forwarded to `loop.create_datagram_endpoint`.
    """
    loop = asyncio.get_event_loop()
    endpoint = endpoint_factory()
    kwargs["remote_addr" if remote else "local_addr"] = host, port
    kwargs["protocol_factory"] = lambda: DatagramEndpointProtocol(endpoint)
    await loop.create_datagram_endpoint(**kwargs)
    return endpoint


async def open_local_endpoint(
    host: str = "0.0.0.0",
    port: int = 0,
    *,
    queue_size: int | None = None,
    **kwargs: dict[str, Any]
) -> Any:
    """Open and return a local datagram endpoint.

    An optional queue size arguement can be provided.
    Extra keyword arguments are forwarded to `loop.create_datagram_endpoint`.
    """
    return await open_datagram_endpoint(
        host,
        port,
        remote=False,
        endpoint_factory=lambda: LocalEndpoint(queue_size),
        **kwargs
    )


async def open_remote_endpoint(
    host: str, port: int, *, queue_size: int | None = None, **kwargs: dict[str, Any]
) -> Any:
    """Open and return a remote datagram endpoint.

    An optional queue size arguement can be provided.
    Extra keyword arguments are forwarded to `loop.create_datagram_endpoint`.
    """
    return await open_datagram_endpoint(
        host,
        port,
        remote=True,
        endpoint_factory=lambda: RemoteEndpoint(queue_size),
        **kwargs
    )
