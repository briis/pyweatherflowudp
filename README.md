# pyweatherflowudp

An event-based asynchronous library to read UDP packets from Weatherflow weather systems on a local network without any reliance on the cloud.

The atomic data provided by WeatherFlow sensors is all natively metric. To help facilitate transformations to other units or to perform calculations and comparisons, this module utilizes [Pint](https://pint.readthedocs.io/en/stable/)'s Quantity class as the type of most properties which have a unit of measurement. See the [Properties](#Properties) section below for more details.

This module utilizes [MetPy](https://unidata.github.io/MetPy/latest/index.html) to help with additional weather calculations that are derived from the various data points provided by the actual WeatherFlow sensors. While WeatherFlow has these additional data points available via the app and rest API, they are unavailable via the low-level UDP packet data. And while a list of [derived metrics](https://weatherflow.github.io/Tempest/api/derived-metric-formulas.html) and the associated equations has been posted, they can be quite complex to implement. As such, MetPy is an invaluable resource since the work has already been done and it eliminates the need to write all the equations in this module (and potentially get them wrong). You may notice that some of these values aren't an exact match with what is shown in the WeatherFlow app because there are different formulas (some simpler, some more complex) to calculate derived weather metrics. This is because WeatherFlow and MetPy may have chosen one of the sometimes many different formulas to get the result desired. They should still be relatively close, however.

## Supported Devices

- Tempest
- Air (untested)
- Sky (untested)

## Usage

The primary way of interacting with this module, and the devices that are found with it, is via event subscriptions.

The classes and events which they currently support are outlined below, but you can also see an example tying this altogether in [demo.py](/demo.py).

### Client

#### `WeatherFlowListener`

- EVENT_DEVICE_DISCOVERED - emitted when a new device (Hub, Air, Sky or Tempest) is disovered for the first time

The classes and events in this section can be imported from `pyweatherflowudp.client`.

### Devices

#### `HubDevice`

- EVENT_LOAD_COMPLETE - emitted once when the hub has finished parsing a status update for the first time
- EVENT_STATUS_UPDATE - emitted each time a status update has been parsed by the hub, including immediately following an EVENT_LOAD_COMPLETE

#### `WeatherFlowSensorDevice` (base class for `AirDevice`, `SkyDevice` and `TempestDevice`)

- EVENT_LOAD_COMPLETE - emitted once when the sensor has finished parsing one status update and one observation for the first time
- EVENT_OBSERVATION - emitted each time an observation has been parsed by the sensor
- EVENT_STATUS_UPDATE - emitted each time a status update has been parsed by the sensor

#### `AirSensorType` (`AirDevice` / `TempestDevice`)

- EVENT_STRIKE - emitted when a lightning strike has been detected

#### `SkySensorType` (`SkyDevice` / `TempestDevice`)

- EVENT_RAIN_START - emitted when rain has been detected
- EVENT_RAPID_WIND - emitted every 3 seconds (or less frequently depending on battery voltage) to inform about current wind condtions

The classes and events in this section can be imported from `pyweatherflowudp.device`.

### Properties

The `pint.Quantity` class has been utilized for device properties which are associated with a unit of measurement. This allows a conversion from the native metric unit to another of the user's choice such as degrees Celsius to degrees Fahrenheit, which produces another `pint.Quantity`:

```python
device.air_temperature.to("degF")
```

To retrieve only the numeric value of a property, you can just append a `.magnitude` (or `.m` short form) like:

```python
device.air_temperature.m
```

You can also retrieve only the units portion of a property with `.units` (or `.u` short form) like:

```python
device.air_temperature.u
```

Check out the [Pint docs](https://pint.readthedocs.io/en/stable/#user-guide) for more tips.
