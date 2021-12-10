# 1.1.1 (2021-12-10)

- Better handling of missing data points when parsing messages which may occure when the firmware revision changes

# 1.1.0 (2021-12-10)

- Deprecated rain_amount_previous_minute due to name/units inconsistency
- Added rain_accumulation_previous_minute, measured in millimeters (mm)
- Added rain_rate, measured in millimeters per hour (mm/hr)
- Added wind_direction_cardinal to indicate the wind direction based on a 16-wind compass rose.

# 1.0.1 (2021-12-02)

Replaces the MetPy package with a combination of PsychroLib and coded equations.

# 1.0.0 (2021-12-01)

The pyweatherflowudp module has been completely rewritten. As such, any version prior to 1.0.0 is incompatible with the new release.
