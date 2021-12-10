# pyweatherflowudp

An event-based asynchronous library to read UDP packets from Weatherflow weather systems on a local network without any reliance on the cloud.

The atomic data provided by WeatherFlow sensors is all natively metric. To help facilitate transformations to other units or to perform calculations and comparisons, this module utilizes [Pint](https://pint.readthedocs.io/en/stable/)'s Quantity class as the type of most properties which have a unit of measurement. See the [Quantity](#Quantity) section below for more details.

This module utilizes [PsychroLib](https://github.com/psychrometrics/psychrolib) to help with additional weather calculations that are derived from the various data points provided by the actual WeatherFlow sensors. While WeatherFlow has these additional data points available via the app and rest API, they are unavailable via the low-level UDP packet data. And while a list of [derived metrics](https://weatherflow.github.io/Tempest/api/derived-metric-formulas.html) and the associated equations has been posted, they can be quite complex to implement, such as calculating wet bulb temperature. As such, PsychroLib is an invaluable resource since the work has already been done and it eliminates the need to write all the equations in this module (and potentially get them wrong). You may notice that some of these values aren't an exact match with what is shown in the WeatherFlow app because there are different formulas (some simpler, some more complex) to calculate derived weather metrics. This is because WeatherFlow and PsychroLib may have chosen one of the sometimes many different formulas to get the result desired. They should still be relatively close, however.

[![DOI](https://joss.theoj.org/papers/10.21105/joss.01137/status.svg)](https://doi.org/10.21105/joss.01137) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2537945.svg)](https://doi.org/10.5281/zenodo.2537945)

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

## Properties

### WeatherFlowListener

| property     | type | description                                                                              |
| ------------ | ---- | ---------------------------------------------------------------------------------------- |
| devices      | list | The known devices.                                                                       |
| hubs         | list | The known hubs.                                                                          |
| is_listening | bool | `True` if the listener is currently monitoring UDP packets on the network, else `False`. |
| sensors      | list | The known sensors.                                                                       |

### WeatherFlowDevice

Base for hubs and sensors.

| property          | type     | description                                                         |
| ----------------- | -------- | ------------------------------------------------------------------- |
| firmware_revision | str      | The current firmware revision of the device.                        |
| load_complete     | bool     | `True` if the device has parsed all initial updates, else `False`.  |
| model             | str      | The model of the device ("Hub", "Air", "Sky", "Tempest").           |
| rssi              | Quantity | The signal strength of the device in decibels.                      |
| serial_number     | str      | The serial number of the device.                                    |
| timestamp         | datetime | The UTC timestamp from the last status update.                      |
| up_since          | datetime | The UTC timestamp the device started up and has since been running. |
| uptime            | int      | The number of seconds the device has been up and running.           |

### HubDevice

| property    | type | description                         |
| ----------- | ---- | ----------------------------------- |
| reset_flags | list | The current reset flags of the hub. |

### WeatherFlowSensorDevice

Base for sensors.

| property        | type     | description                                           |
| --------------- | -------- | ----------------------------------------------------- |
| battery         | Quantity | The current battery voltage.                          |
| hub_rssi        | Quantity | The signal strength of the hub in decibels.           |
| hub_sn          | str      | The serial number of the hub the sensor belongs to.   |
| last_report     | datetime | The UTC timestamp from the last observation.          |
| sensor_status   | list     | The list of issues the sensor is currently reporting. |
| report_interval | Quantity | The report interval in minutes.                       |
| reset_flags     | list     | The current reset flags of the hub.                   |

### AirSensorType

Base for "air" sensor measurements (Air/Tempest).

| property                                   | type                 | description                                                            |
| ------------------------------------------ | -------------------- | ---------------------------------------------------------------------- |
| air_temperature                            | Quantity             | The current air temperature in degrees Celsius.                        |
| last_lightning_strike_event                | LightningStrikeEvent | The last lightning strike event.                                       |
| lightning_strike_average_distance          | Quantity             | The average distance for lightning strikes in kilometers.              |
| lightning_strike_count                     | int                  | The number of lightning strikes.                                       |
| relative_humidity                          | Quantity             | The relative humidity percentage.                                      |
| station_pressure                           | Quantity             | The observed station pressure in millibars.                            |
| air_density\*                              | Quantity             | The calculated air density in kilograms per cubic meter.               |
| delta_t\*                                  | Quantity             | The calculated Delta T in delta degrees Celsius.                       |
| dew_point_temperature\*                    | Quantity             | The calculated dew point temperature in degrees Celsius.               |
| heat_index\*                               | Quantity             | The calculated heat index in degrees Celsius.                          |
| vapor_pressure\*                           | Quantity             | The calculated vapor pressure in millibars.                            |
| wet_bulb_temperature\*                     | Quantity             | The calculated wet bulb temperature in degrees Celsius.                |
| _calculate_sea_level_pressure(height)_\*\* | Quantity             | Calculate the sea level pressure in millibars from a specified height. |

\* Indicates derived properties

\*\* Indicates this is a method, not a property.

### SkySensorType

Base for "sky" sensor measurements (Sky/Tempest).

| property                          | type              | description                                                                        |
| --------------------------------- | ----------------- | ---------------------------------------------------------------------------------- |
| illuminance                       | Quantity          | The current illuminance in Lux.                                                    |
| last_rain_start_event             | RainStartEvent    | The last rain start event.                                                         |
| last_wind_event                   | WindEvent         | The last wind event.                                                               |
| precipitation_type                | PrecipitationType | The current precipitation type: (NONE, RAIN, HAIL or RAIN_HAIL).                   |
| rain_accumulation_previous_minute | Quantity          | The rain accumulation from the previous minute in millimeters.                     |
| rain_rate\*                       | Quantity          | The rain rate in millimeters per hour (based on the previous minute accumulation). |
| solar_radiation                   | Quantity          | The solar radiation in Watts per cubic meter.                                      |
| uv                                | int               | The current UV index.                                                              |
| wind_average                      | Quantity          | The wind speed average over the report interval in meters per second.              |
| wind_direction                    | Quantity          | The wind direction over the report interval in degrees.                            |
| wind_direction_cardinal           | string            | The wind direction cardinal (16-wind compass rose).                                |
| wind_gust                         | Quantity          | The wind gust (maximum 3 second sample) in meters per second.                      |
| wind_lull                         | Quantity          | The wind lull (minimum 3 second sample) in meters per second.                      |
| wind_sample_interval              | Quantity          | The wind sample interval in seconds.                                               |
| wind_speed                        | Quantity          | The wind speed in meters per second.                                               |

\* Indicates derived properties

### TempestDevice

| property                 | type     | description                                                 |
| ------------------------ | -------- | ----------------------------------------------------------- |
| feels_like_temperature\* | Quantity | The calculated "feels like" temperature in degrees Celsius. |
| wind_chill_temperature\* | Quantity | The calculated wind chill temperature in degrees Celsius.   |

\* Indicates derived properties

### Quantity

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
