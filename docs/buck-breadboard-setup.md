# Buck converter bench test

Third bench test: confirm the MP1584EN regulates a stepped-down output before you ever connect the 18650 pack.

## You need

- ESP32-C3 board + USB-C cable
- Breadboard and jumper wires
- MP1584EN buck converter module
- Multimeter

Do **not** connect the 18650 pack, the servo, or the DRV8833 yet.

## Goal

Power the buck from the ESP32-C3's 5 V rail (USB power), measure the output, and dial the trimpot to a known voltage. This proves the module works and teaches you the trimming feel before any battery is involved.

## Wiring

| From | To |
|---|---|
| ESP32-C3 5V / VBUS | Buck **IN+** |
| ESP32-C3 GND | Buck **IN-** |
| Multimeter (V) | Buck **OUT+** to **OUT-** |

If the module has duplicate pads on each terminal, those are the same node — use whichever is convenient.

## Important: a buck only steps down

With ~5 V at the input, the output **must** be lower than ~5 V (the regulator needs headroom). For this USB-powered test, target one of:

- **3.3 V** — confirms it regulates down cleanly.
- **4.0 V** — confirms it still regulates near the top of its range.

Don't try to dial 5 V here — you'd be running the regulator out of headroom.

## Procedure

1. Wire IN+ / IN- only. Leave OUT+ / OUT- going only to the multimeter.
2. Plug in the ESP32-C3 (USB power).
3. Read the output. Adjust the trimpot **slowly** with a small screwdriver until you hit your target.

> [!NOTE]
> The MP1584EN can read unstable on the multimeter at no load — values can drift. Putting a 220 Ω–330 Ω resistor across OUT+ / OUT- gives the regulator something to push against and the reading settles. Real loads (DRV8833, servo) do the same thing.

## Don't

- Don't tie the buck output back into the ESP32-C3's 5 V pin while the board is also USB-powered. You'd be fighting two sources on the same rail.
- Don't connect both the 18650 pack and USB to the same rail simultaneously.
- Don't trim the buck without a multimeter on the output.

## Once it regulates cleanly

That's it for this bench step. The next stage is wiring the buck on the battery side, in this order:

```
18650 pack → reverse-polarity board → polyfuse → buck IN → buck OUT (5 V) → ESP32-C3, servo, DRV8833 logic
                                                          ↘ raw battery → DRV8833 VM (motor power)
```

Set the output back to **5.0 V** once you're powering it from the 2S 18650 pack (8.4 V down to 6.4 V), and re-measure under load before connecting anything sensitive.
