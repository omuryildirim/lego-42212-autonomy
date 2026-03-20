# N20 Breadboard Setup

This is the next bench test after the servo check.

Open the editable diagram in:
- [docs/n20-breadboard-setup.drawio](d:\Projects\autonomous-lego-42212\docs\n20-breadboard-setup.drawio)

Use:
- ESP32-C3 board over USB-C
- Breadboard
- DRV8833 breakout
- One GA-N20 motor
- Jumper wires

Do not connect yet:
- 18650 battery pack
- MP1584EN

Optional for this test:
- leave the servo disconnected

## Goal

Test only motor direction control first.

## Firmware pin mapping

Current firmware uses:
- GPIO 4 -> DRV8833 IN1
- GPIO 5 -> DRV8833 IN2

Use one half of the DRV8833.

Typical DRV8833 labels on a breakout:
- IN1 / IN2 or AIN1 / AIN2
- OUT1 / OUT2 or AOUT1 / AOUT2
- VM
- GND

If your breakout also has `nSLEEP` or `SLP`, tie it high if the board does not already do that.

## Breadboard wiring

1. Connect ESP32-C3 GND to the breadboard ground rail.
2. Connect DRV8833 GND to the same ground rail.
3. Connect ESP32-C3 5V or VBUS to the DRV8833 VM input for this short bench test.
4. Connect GPIO 4 to DRV8833 IN1.
5. Connect GPIO 5 to DRV8833 IN2.
6. Connect the N20 motor leads to DRV8833 OUT1 and OUT2.

If the motor direction is reversed from what you want, swap the two motor wires.

## Wiring diagram

### Simple connection map

```text
Laptop USB
   |
   | USB-C cable
   v
ESP32-C3

5V / VBUS  ---------------------> DRV8833 VM
GND        ---------------------> DRV8833 GND
GPIO 4     ---------------------> DRV8833 IN1
GPIO 5     ---------------------> DRV8833 IN2

DRV8833 OUT1 -------------------> N20 motor lead 1
DRV8833 OUT2 -------------------> N20 motor lead 2
```

### Quick bench layout

```text
ESP32-C3 USB-C -> laptop USB

ESP32-C3 GND   -> breadboard GND rail
ESP32-C3 5V    -> DRV8833 VM
ESP32-C3 GPIO4 -> DRV8833 IN1
ESP32-C3 GPIO5 -> DRV8833 IN2

DRV8833 GND    -> breadboard GND rail
DRV8833 OUT1   -> N20 lead 1
DRV8833 OUT2   -> N20 lead 2
```

## Important limits

- Do not connect the motor directly to an ESP32 pin.
- Do not connect the motor directly to 3V3.
- Keep the grounds common.
- Use USB power only for short no-load tests.
- Keep the motor unloaded for this first test.
- Do not stall the motor.

## What USB power is good for

USB is fine for a quick first test if:
- the motor is not driving the car yet
- the motor shaft spins freely
- you only use short bursts

USB is not the final power setup.

## Before power on

Check:
- DRV8833 GND and ESP32 GND are connected
- DRV8833 VM is on 5V or VBUS
- GPIO 4 goes to IN1
- GPIO 5 goes to IN2
- motor wires go only to OUT1 and OUT2
- battery pack is not connected

## First test flow

1. Disconnect the servo if you want the cleanest motor test.
2. Wire ESP32-C3, DRV8833, and N20 only.
3. Connect the ESP32-C3 by USB-C.
4. Flash the firmware.
5. Start the keyboard bridge.
6. Tap `W` briefly.
7. Tap `S` briefly.

For this test, avoid holding the key down for long.

## Expected behavior

- `W` should spin the motor one direction.
- `S` should spin the motor the other direction.
- releasing the key should stop the motor.

## If the motor does not move

Check in this order:

1. DRV8833 VM has 5V.
2. Grounds are shared.
3. IN1 is on GPIO 4.
4. IN2 is on GPIO 5.
5. Motor leads are on OUT1 and OUT2.
6. Keyboard bridge is connected and sending commands.

## If the ESP32-C3 resets

This usually means USB power or wiring is not stable enough.

Try:
- disconnect the servo during the motor test
- test the motor with no load
- use shorter bursts
- check for wiring mistakes or shorts

If that still happens, move the motor to a separate regulated supply later and keep GND shared.

## Next step after motor test

After the motor test is stable, add the servo back and then move to the battery and buck regulator stage.