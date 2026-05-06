# Documentation

## Bench tests

Work through these in order before integrating onto the LEGO chassis. Each step adds one component to the previous setup.

1. [Servo bench test](servo-breadboard-setup.md) — drive the SG90 from USB-powered ESP32-C3.
2. [N20 + DRV8833 bench test](n20-breadboard-setup.md) — add the motor driver and one N20.
3. [Buck converter bench test](buck-breadboard-setup.md) — verify the MP1584EN before connecting the 18650 pack.

Editable diagrams: [servo-breadboard-setup.drawio](servo-breadboard-setup.drawio), [n20-breadboard-setup.drawio](n20-breadboard-setup.drawio).

## Control

- [BLE control](ble-setup.md) — interface flags, command grammar, BLE UUIDs, troubleshooting.
- [Desktop keyboard bridge](../tools/README.md) — running `keyboard_control.py` in serial or BLE mode.
- [Steering calibration](steering-calibration.md) — `kServoSide` and `kSteeringTrim` tuning once the servo is on the chassis.

## Mechanical

- [3D-printed adapters](3d-printing/README.md) — couplers from SG90, EMax ES08MA II, and GA12-N20 shafts to LEGO Technic axles.
