"""Test helpers."""
from __future__ import annotations

import pytest
from pint import Quantity

from pyweatherflowudp.const import UNIT_DEGREES, units
from pyweatherflowudp.helpers import degrees_to_cardinal


@pytest.mark.parametrize(
    "degrees,cardinal",
    [
        (0, "N"),
        (22.5, "NNE"),
        (45, "NE"),
        (67.5, "ENE"),
        (90, "E"),
        (112.5, "ESE"),
        (135, "SE"),
        (157.7, "SSE"),
        (180, "S"),
        (202.5, "SSW"),
        (225, "SW"),
        (247.5, "WSW"),
        (270, "W"),
        (292.5, "WNW"),
        (315, "NW"),
        (337.5, "NNW"),
        (units.Quantity(360, UNIT_DEGREES), "N"),
    ],
)
def test_degrees_to_cardinal(degrees: float | Quantity[float], cardinal: str) -> None:
    """Test conversion of degrees to cardinal."""
    assert degrees_to_cardinal(degrees) == cardinal
