"""Errors for WeatherFlow UDP connections."""


class WeatherflowUdpError(Exception):
    """Base WeatherFlow UDP error."""


class ListenerError(WeatherflowUdpError):
    """Error indicating a proplem with the listener."""


class AddressInUseError(ListenerError):
    """Error indicating the listener address is already in use."""


class EndpointError(ListenerError):
    """Error indicating an issue with the UDP endpoint."""
