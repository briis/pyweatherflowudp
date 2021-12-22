"""Sensor fault singleton."""
from __future__ import annotations


class SensorFault:  # pylint: disable=too-few-public-methods
    """Sensor fault singleton."""

    _instance: SensorFault | None = None

    def __new__(cls) -> SensorFault:
        """Return an instance of SensorFault."""
        if cls._instance is None:
            cls._instance = super(SensorFault, cls).__new__(cls)
        return cls._instance


SENSOR_FAULT = SensorFault()
