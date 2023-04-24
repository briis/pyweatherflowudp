"""Test calculations."""
from pyweatherflowudp.calc import heat_index
from pyweatherflowudp.const import UNIT_DEGREES_CELSIUS, UNIT_PERCENT


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
