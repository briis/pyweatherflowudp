"""Test the module version."""

from pyweatherflowudp import __version__


def test_version() -> None:
    """Test version."""
    assert __version__ == "1.4.5"
