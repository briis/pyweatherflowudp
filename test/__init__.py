"""Provide tests for pyweatherflowudp."""
import pathlib


def load_fixture(name) -> str:
    """Load a fixture."""
    return (pathlib.Path(__file__).parent / "fixtures" / name).read_text()
