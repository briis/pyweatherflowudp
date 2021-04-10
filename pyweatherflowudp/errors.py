"""Define package errors."""


class WeatherflowUdpError(Exception):
    """Define a base error."""


class RequestError(WeatherflowUdpError):
    """Define an error related to invalid requests."""


class ResultError(WeatherflowUdpError):
    """Define an error related to the result returned from a request."""
