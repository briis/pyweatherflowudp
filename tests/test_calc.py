"""Test calculations."""

from pyweatherflowudp.calc import (
    alkaline_battery_soc,
    lto_battery_soc,
    heat_index,
    vapor_pressure,
)
from pyweatherflowudp.const import (
    UNIT_DEGREES_CELSIUS,
    UNIT_MILLIBARS,
    UNIT_PERCENT,
    UNIT_VOLTS,
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


def test_alkaline_battery_soc() -> None:
    """Test the battery voltage to percentage calculations."""

    # below minimum
    assert alkaline_battery_soc(0.5 * UNIT_VOLTS) == 0 * UNIT_PERCENT
    # at minimum
    assert alkaline_battery_soc(1.1 * UNIT_VOLTS) == 0 * UNIT_PERCENT
    # interpolated
    assert round(alkaline_battery_soc(1.35 * UNIT_VOLTS), 3) == 72.5 * UNIT_PERCENT
    # at maximum
    assert alkaline_battery_soc(1.59 * UNIT_VOLTS) == 100 * UNIT_PERCENT
    # above maximum
    assert alkaline_battery_soc(1.65 * UNIT_VOLTS) == 100 * UNIT_PERCENT


def test_lto_battery_soc() -> None:
    """Test the battery voltage to percentage calculations."""

    # below minimum
    assert lto_battery_soc(1.5 * UNIT_VOLTS) == 0 * UNIT_PERCENT
    # at minimum
    assert lto_battery_soc(2 * UNIT_VOLTS) == 0 * UNIT_PERCENT
    # interpolated
    assert round(lto_battery_soc(2.29 * UNIT_VOLTS), 3) == 62.5 * UNIT_PERCENT
    # at maximum
    assert lto_battery_soc(2.7 * UNIT_VOLTS) == 100 * UNIT_PERCENT
    # above maximum
    assert lto_battery_soc(2.8 * UNIT_VOLTS) == 100 * UNIT_PERCENT


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
