"""Demo"""
import asyncio
import logging

from pyweatherflowudp.client import EVENT_DEVICE_DISCOVERED, WeatherFlowListener
from pyweatherflowudp.const import (
    EVENT_RAIN_START,
    EVENT_RAPID_WIND,
    EVENT_STRIKE,
    units,
)
from pyweatherflowudp.device import (
    EVENT_LOAD_COMPLETE,
    EVENT_OBSERVATION,
    EVENT_STATUS_UPDATE,
    AirSensorType,
    SkySensorType,
    TempestDevice,
    WeatherFlowDevice,
)
from pyweatherflowudp.errors import ListenerError
from pyweatherflowudp.event import CustomEvent, Event

logging.basicConfig(level=logging.INFO)


async def main():
    """Main entry point."""

    def device_discovered(device: WeatherFlowDevice):
        """Handle a discovered device."""
        print("Found device:", device)

        def device_event(event: Event):
            """Handle an event."""
            print(event, "from", device)
            if isinstance(event, CustomEvent) and event.name == EVENT_OBSERVATION:
                if isinstance(device, AirSensorType):
                    # print the air temperature
                    print("Air temperature:", device.air_temperature)
                    # print the air temperature in °F
                    print("Air temperature:", device.air_temperature.to("degF"))
                    # also prints the air temperature in °F
                    print("Air temperature:", device.air_temperature.to(units.degF))

                    # calculate the sea level pressure from a height of 1000 meters
                    print(
                        "Sea level pressure:",
                        device.calculate_sea_level_pressure(units.Quantity(1000, "m")),
                    )
                    # or at 1000 feet
                    print(
                        "Sea level pressure:",
                        device.calculate_sea_level_pressure(
                            units.Quantity(1000, units.foot)
                        ),
                    )
                if isinstance(device, TempestDevice):
                    # print the feels like temperature in °F
                    print(
                        "Feels like temperature:",
                        device.feels_like_temperature.to("degF"),
                    )

        event_lambda = lambda event: device_event(event)
        device.on(EVENT_LOAD_COMPLETE, event_lambda)
        device.on(EVENT_OBSERVATION, event_lambda)
        device.on(EVENT_STATUS_UPDATE, event_lambda)
        if isinstance(device, AirSensorType):
            device.on(EVENT_STRIKE, event_lambda)
        if isinstance(device, SkySensorType):
            device.on(EVENT_RAIN_START, event_lambda)
            device.on(EVENT_RAPID_WIND, event_lambda)

    try:
        async with WeatherFlowListener() as client:
            client.on(EVENT_DEVICE_DISCOVERED, lambda device: device_discovered(device))
            await asyncio.sleep(60)
    except ListenerError as ex:
        print(ex)


if __name__ == "__main__":
    asyncio.run(main())
