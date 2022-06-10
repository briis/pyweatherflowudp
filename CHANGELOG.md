# Unreleased

- Bump Pint to ^0.19

## Potential Breaking Change:

- The default symbol for hour in Pint 0.19 is now "h" instead of "hr" - https://github.com/hgrecco/pint/pull/1454

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
