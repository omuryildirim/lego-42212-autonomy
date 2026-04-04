# Buck Breadboard Setup

This is the next bench step after the N20 motor test.

Use this stage to verify that the buck converter works, learn how to wire it, and set its output safely before the first 18650 battery test.

## Goal

Do a low-risk bench check of the buck module on the breadboard.

For this first check:
- power the buck input from the ESP32-C3 USB 5V or VBUS rail
- measure the buck output with a multimeter
- do not power the car through the buck yet
- do not connect the 18650 pack yet

## Important limitation

A buck converter only steps voltage down.

That means:
- if the input is about 5V from USB, the output must be lower than 5V
- this USB-powered test is good for verifying the module and adjusting it
- this USB-powered test is not the final 5V supply plan for the servo and car

For the future battery setup, the intended flow is:
- 2S 18650 pack -> protection -> buck input
- buck output -> regulated low-voltage rail

## Use

- ESP32-C3 board over USB-C
- Breadboard
- Buck converter module such as MP1584EN
- Jumper wires
- Multimeter

Do not connect yet:
- 18650 battery pack
- servo power to the buck output
- DRV8833 VM to the buck output

## First bench wiring

1. Connect ESP32-C3 GND to the breadboard ground rail.
2. Connect ESP32-C3 5V or VBUS to the buck `IN+`.
3. Connect ESP32-C3 GND to the buck `IN-`.
4. Leave `OUT+` and `OUT-` disconnected from the rest of the project.
5. Put a multimeter across `OUT+` and `OUT-`.

If the module has duplicate pads for each terminal, the duplicate holes are normally the same electrical node.

## Simple connection map

```text
Laptop USB
   |
   | USB-C cable
   v
ESP32-C3

5V / VBUS  ---------------------> Buck IN+
GND        ---------------------> Buck IN-

Multimeter + -------------------> Buck OUT+
Multimeter - -------------------> Buck OUT-
```

## What to do next

1. Power the ESP32-C3 from USB.
2. Measure the buck output with the multimeter.
3. Adjust the trim potentiometer slowly.
4. Set the output to a safe test voltage such as `3.3V` or `4.0V`.

For this USB-powered bench step, do not try to set the output to 5V. With a 5V input rail there is not enough headroom for a proper 5V regulated output.

As a next step you can connect buck outputs to DRV8833. If you do so keep the test brief.

> [!NOTE]  
> The buck might not regulate cleanly at no load, meaning that when you read outputs via multimeter, readings can change with time.
> If buck is connected to a resistor or the driver multimeter reading will become stable.
> If you want to test the buck with a resistor connect it between `OUT+` and `OUT-`. A `220 ohm` or `330 ohm` resistor should be enough for testing this setup.

## Do not do these yet

- Do not connect the buck output back into the ESP32-C3 5V pin while the board is already powered from USB.
- Do not connect the 18650 pack and USB input to the same power rail at the same time.
- Do not adjust the buck without a multimeter.

## Safe first targets

Reasonable first output targets for this USB-only test:

- `3.3V` to confirm the module regulates down correctly
- `4.0V` if you want to confirm it still regulates near the top end

Do not connect the servo or motor while doing the first trim adjustment.

## Before moving to 18650

Before the first battery-powered test, the preferred order is:

1. battery pack with protection
2. polyfuse
3. reverse-polarity protection
4. buck input
5. measure and set buck output before connecting loads

## Suggested next step after this check

After the buck module is confirmed working on USB input, the next step is a first 18650-powered buck setup with no motor load and the output measured again before connecting the rest of the system.