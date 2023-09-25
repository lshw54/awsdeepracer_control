# awsdeepracer_control
 This python package rewrite to support the new version Deepracer Console Software ```version 2.0.383.0```

# What's New
- Compatibility with Deepracer Console Software version 2.0.383.0.
- Resolved the issue where the video stream was not displayed.
- Updated the move method to support the new version of the web console.
- Removed the following methods: move_forward, move_backward, turn_right, turn_left.
- Added robust error handling for scenarios like unreachable vehicle, inaccessible CSRF token, and incorrect credentials.
- Enhanced security checks in API calls to ensure the accuracy of success statuses.
- Addressed potential Python identifier issues, such as replacing null with None.

# Package Repo Link
https://github.com/lshw54/awsdeepracer_control

# Package Pypi Link
https://pypi.org/project/awsdeepracer-control/

# API

## High level methods
* show_vehicle_info
* move

## General purpose methods
* get_is_usb_connected
* get_battery_level
* get_raw_video_stream

## Methods for running autonomous mode
* set_autonomous_mode
* set_throttle_percent

## methods for running manual mode
* set_manual_mode
* start_car
* stop_car
* move

## methods for models
* get_models
* get_uploaded_models
* load_model
* upload_model

## methods for calibration
* set_calibration_mode
* get_calibration_angle
* get_calibration_throttle
* set_calibration_throttle
* set_calibration_angle

# Installation
```
pip install awsdeepracer_control
```

# Getting Started

## Show vehicle info

```python
import awsdeepracer_control

client = awsdeepracer_control.Client(password="???", ip="111.222.333.444")
client.show_vehicle_info()
```

# Others

This repo is rewrite from :
* https://github.com/thu2004/deepracer-vehicle-api/