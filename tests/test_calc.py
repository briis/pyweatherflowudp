"""Test calculations."""
from pyweatherflowudp.calc import heat_index
from pyweatherflowudp.const import UNIT_DEGREES_CELSIUS, UNIT_PERCENT


def test_heat_index() -> None:
    """Test the heat_index calculations."""
    temp_degC = 30 * UNIT_DEGREES_CELSIUS
    relative_humidity = 10 * UNIT_PERCENT
    assert (
        round(heat_index(temp_degC, relative_humidity), 5)
        == 27.86179 * UNIT_DEGREES_CELSIUS
    )

    relative_humidity = 90 * UNIT_PERCENT
    assert (
        round(heat_index(temp_degC, relative_humidity), 5)
        == 40.77465 * UNIT_DEGREES_CELSIUS
    )

    temp_degC = 10 * UNIT_DEGREES_CELSIUS
    assert heat_index(temp_degC, relative_humidity) is None
