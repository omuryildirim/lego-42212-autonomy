# SG90 Breadboard Setup

This is the simplest first test setup.

Open the editable diagram in:
- [docs/servo-breadboard-setup.drawio](d:\Projects\autonomous-lego-42212\docs\servo-breadboard-setup.drawio)

Use:
- ESP32-C3 board over USB-C
- Breadboard
- SG90 servo
- Jumper wires

Do not connect yet:
- DRV8833
- GA-N20 motor
- MP1584EN
- 18650 battery pack

## Goal

Test only steering movement first.

## Pin mapping

Current firmware uses:
- GPIO 6 -> SG90 signal

From the servo side:
- Orange or yellow -> signal
- Red -> +5V
- Brown or black -> GND

## Breadboard wiring

1. Connect the ESP32-C3 to the breadboard ground rail.
2. Connect the servo ground wire to the same ground rail.
3. Connect the servo signal wire to ESP32-C3 GPIO 6.
4. Connect the servo red wire to the board 5V or VBUS pin.

## Wiring diagram

### Simple connection map

```text
Laptop USB
	 |
	 | USB-C cable
	 v
ESP32-C3

5V / VBUS  ---------------------> SG90 red
GND        ---------------------> SG90 brown/black
GPIO 6     ---------------------> SG90 orange/yellow
```

### Breadboard view

```text
Top power rail:    +++++++++++++++++++++++++++++++++++++++++   +5V
Bottom power rail: -----------------------------------------   GND

								 ESP32-C3 board
				+---------------------------------+
 USB-C  |                                 |
 =====> | [5V] [GND] [ ... ] [GPIO6]      |
				+---|-----|---------------|-------+
						|     |               |
						|     |               +--------------------+
						|     +--------------------------------+   |
						+-------------------------------+      |   |
																						|      |   |
Top power rail:    ++++++++++++++++++++++++++------+---+   +5V
Bottom power rail: --------------------------+----------   GND

Servo:
	red    -> top +5V rail
	brown  -> bottom GND rail
	orange -> GPIO 6 jumper
```

For an editable version, use the draw.io file linked above.

### Servo lead view

```text
SG90 wire colors

orange/yellow = signal
red           = +5V
brown/black   = GND
```

## Important limits

- Do not connect the servo red wire to 3V3.
- Do not connect the servo red wire to a GPIO pin.
- Keep the grounds common.
- For a light bench test, USB power is usually enough.
- If the ESP32-C3 resets when the servo moves, stop and move servo power to a separate 5V supply.

## Suggested first bench layout

```text
ESP32-C3 USB-C -> laptop USB

ESP32-C3 GND  -> breadboard GND rail
ESP32-C3 5V   -> breadboard +5V rail
ESP32-C3 GPIO6 -> SG90 signal

SG90 brown/black -> breadboard GND rail
SG90 red         -> breadboard +5V rail
SG90 orange      -> ESP32-C3 GPIO6
```

## Before power on

Check:
- servo ground and ESP32 ground are connected
- servo signal is on GPIO 6
- servo power is on 5V, not 3V3
- no motor driver is connected yet

## First test flow

1. Wire the servo only.
2. Connect the ESP32-C3 by USB-C.
3. Flash the firmware.
4. Start the keyboard bridge.
5. Press `A` and `D` only.

For this first test, avoid `W` and `S` since no drive motor is connected.

## Expected behavior

- At startup, the servo should move to center.
- Pressing `A` should steer one direction.
- Pressing `D` should steer the other direction.
- Releasing keys should return steering toward center.

## If the servo does not move

Check in this order:

1. Servo has 5V power.
2. Grounds are shared.
3. Signal wire is on GPIO 6.
4. Firmware is flashed successfully.
5. Keyboard bridge is connected to the correct COM port.

## If the ESP32-C3 resets

This usually means USB power is not enough for servo current spikes.

Try:
- move the servo horn by hand to reduce load before power-on
- test without any linkage attached
- add a separate 5V servo supply later
- keep GND shared between servo supply and ESP32-C3

## Next step after servo test

After the servo test is stable, add the DRV8833 and GA-N20 motor on a separate wiring step.