# Documentation

These docs follow the recommended three-stage build (per-component bench → breadboard motherboard → perfboard), plus reference material for control software and mechanical bits. See the main [README](../README.md) for the high-level plan and bill of materials.

## Per-component bench tests

Each module verified on a breadboard from USB power, in order. Don't skip ahead.

1. [Servo bench test](servo-breadboard-setup.md): SG90 driven from a USB-powered ESP32-C3.
2. [N20 + DRV8833 bench test](n20-breadboard-setup.md): single motor through the H-bridge.
3. [Buck converter bench test](buck-breadboard-setup.md): MP1584EN verified before the 18650 pack goes anywhere near it.
4. **Full motherboard on a breadboard.** No separate doc; wire up the [perfboard layout](perfboard-layout.md) in jumper wires, mount the motors on the LEGO chassis, and test the steering and backwheel movmement from battery power. The most important sanity check before soldering: mechanical, hardware, and software all working end-to-end.

Editable diagrams: [servo-breadboard-setup.drawio](servo-breadboard-setup.drawio), [n20-breadboard-setup.drawio](n20-breadboard-setup.drawio).

## Perfboard motherboard

- [Perfboard layout](perfboard-layout.md): 40×60 mm board with cell-by-cell placement, color-coded wiring, and critical assembly notes. Build a breadboard version of this layout first (drive the car around from battery power) before committing anything to solder.

## Control

- [BLE control](ble-setup.md): interface flags, command grammar, BLE UUIDs, troubleshooting.
- [Desktop keyboard bridge](../tools/README.md): running `keyboard_control.py` in serial or BLE mode.

## Mechanical

- [3D-printed adapters](3d-printing/README.md): couplers from SG90, EMax ES08MA II, and GA12-N20 shafts to LEGO Technic axles.
- [Steering calibration](steering-calibration.md): `kServoSide` and `kSteeringTrim` tuning once the servo is on the chassis.
