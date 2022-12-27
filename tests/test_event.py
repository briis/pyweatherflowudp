"""Test the module version."""
from datetime import datetime, timezone

from pyweatherflowudp.event import CustomEvent


def test_custom_event() -> None:
    """Test custom event."""
    timestamp = datetime.now(timezone.utc).timestamp()
    event = CustomEvent(timestamp, "Test")
    assert event.epoch == timestamp
    assert event.timestamp == datetime.fromtimestamp(timestamp, timezone.utc)
    assert event.name == "Test"
