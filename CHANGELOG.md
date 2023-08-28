# 1.4.4 (2023-08-28)

- Add `power_save_mode` property to Tempest devices

# 1.4.3 (2023-08-13)

- Support Pint >=0.19

# 1.4.2 (2023-04-24)

- Adjusted logic for `heat_index` to match [WeatherFlow documentation](https://weatherflow.github.io/Tempest/api/derived-metric-formulas.html#heat-index)
- Add `feels_like_temperature` to calc.py

# 1.4.1 (2022-07-11)

- Adjusted logic for calculate_sea_level_pressure to match [WeatherFlow documentation](https://weatherflow.github.io/Tempest/api/derived-metric-formulas.html#sea-level-pressure)

# 1.4.0 (2022-06-10)

- Adjusted logic for `wind_direction` and `wind_direction_cardinal` to report based on the last wind event or observation, whichever is most recent (similar to `wind_speed`)
- Added properties for `wind_direction_average` and `wind_direction_average_cardinal` to report only on the average wind direction
- Handle UnicodeDecodeError during message processing
- Bump Pint to ^0.19

## Breaking Changes:

- The properties `wind_direction` and `wind_direction_cardinal` now report based on the last wind event or observation, whichever is most recent. If you want the wind direction average (previous logic), please use the properties `wind_direction_average` and `wind_direction_average_cardinal`, respectively
- The default symbol for `rain_rate` is now `mm/h` instead of `mm/hr` due to Pint 0.19 - https://github.com/hgrecco/pint/pull/1454

# 1.3.1 (2022-06-01)

- Handle up_since oscillation on devices
- Rename private initialization variables in device class for clarity

# 1.3.0 (2021-12-22)

- Add cloud base and freezing level calculations
- Rename parameter `height` to `altitude` on calculate_sea_level_pressure
  - Works with named height parameter still, but will produce a warning and eventually be dropped

# 1.2.0 (2021-12-21)

## Potential Breaking Change:

- Most sensor properties now return `None` if the value is unknown instead of a default.

# 1.1.2 (2021-12-18)

- Handle null wind values on observations, which happens during low voltage mode
- Fix units associated with wind_sample_interval (was erroneously in minutes, now correctly in seconds)

# 1.1.1 (2021-12-10)

- Better handling of missing data points when parsing messages which may occur when the firmware revision changes

# 1.1.0 (2021-12-10)

- Deprecated rain_amount_previous_minute due to name/units inconsistency
- Added rain_accumulation_previous_minute, measured in millimeters (mm)
- Added rain_rate, measured in millimeters per hour (mm/hr)
- Added wind_direction_cardinal to indicate the wind direction based on a 16-wind compass rose

# 1.0.1 (2021-12-02)

Replaces the MetPy package with a combination of PsychroLib and coded equations.

# 1.0.0 (2021-12-01)

The pyweatherflowudp module has been completely rewritten. As such, any version prior to 1.0.0 is incompatible with the new release.
