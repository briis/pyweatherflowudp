"""Test calculations."""
from pyweatherflowudp.calc import heat_index, vapor_pressure
from pyweatherflowudp.const import (
    UNIT_DEGREES_CELSIUS,
    UNIT_MILLIBARS,
    UNIT_PERCENT,
    units,
)


def test_heat_index() -> None:
    """Test the heat_index calculations."""
    temp_degrees = 30 * UNIT_DEGREES_CELSIUS
    relative_humidity = 90 * UNIT_PERCENT

    assert (temp := heat_index(temp_degrees, relative_humidity)) is not None
    assert round(temp, 5) == 40.71909 * UNIT_DEGREES_CELSIUS

    relative_humidity = 10 * UNIT_PERCENT
    assert heat_index(temp_degrees, relative_humidity) is None

    temp_degrees = 10 * UNIT_DEGREES_CELSIUS
    assert heat_index(temp_degrees, relative_humidity) is None


def test_vapor_pressure() -> None:
    """Test the vapor_pressure calculations."""
    temp_degrees = 71.7 * units.degF
    relative_humidity = 55.17 * UNIT_PERCENT

    vap_pressure = vapor_pressure(temp_degrees, relative_humidity)
    assert round(vap_pressure, 3) == 14.641 * UNIT_MILLIBARS
    assert round(vap_pressure.to(units.kPa), 3) == 1.464 * units.kPa

    temp_degrees = 60.0 * units.degF
    relative_humidity = 41.93 * UNIT_PERCENT

    vap_pressure = vapor_pressure(temp_degrees, relative_humidity)
    assert round(vap_pressure, 3) == 7.411 * UNIT_MILLIBARS
    assert round(vap_pressure.to(units.kPa), 3) == 0.741 * units.kPa
