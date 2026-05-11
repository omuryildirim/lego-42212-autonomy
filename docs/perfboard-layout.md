# Perfboard layout (40×60 mm motherboard)

Motherboard that integrates the ESP32-C3 SuperMini, MP1584EN buck, DRV8833, polyfuse, decoupling caps, and the SG90 servo connector on a single 40×60 mm perfboard. The reverse-polarity protection module mounts separately on the chassis (it has no solder pads).

Board: 20 columns × 14 rows (cols `1`–`20`, rows `A`–`N`), each hole isolated, with ~12 entrance pads along each short edge. Rows are printed bottom-to-top on the physical board, so **row A is at the bottom, row N is at the top**. The cell table below matches.

## Components

| Part | Footprint | Notes |
|---|---|---|
| ESP32-C3 SuperMini | cols 13–20, rows D & J (rotated 90° CCW) | Stackable male-female headers |
| MP1584EN buck | cols 1–8, rows B–G | Direct-solder using male-male pin headers |
| DRV8833 (12-pin, single VCC) | cols 1–7, rows I–N | Direct-solder using male-male pin headers. Single VCC pin powers motor *and* logic |
| SG90 3-pin connector | A11 (GND) / A12 (5V) / A13 (Sig) | Cable exits bottom edge |
| Polyfuse | A1 (PF1, load) / A3 (PF2, battery) | 3-cell lead span, body bridges A2 |
| 470 µF / 16 V electrolytic | C11 (−) / C12 (+) | SG90 bulk |
| 47 µF / 25 V electrolytic | K10 (+) / L10 (−) | DRV VCC bulk |
| 100 nF ceramic ×2 | K8 / L8 (DRV) and E11 / E12 (SG90) | No polarity |
| 100 nF ceramic | across N20 motor terminals | Off-board, soldered to the motor tabs themselves |

ESP32 mounts components-face up (antenna, USB-C, BOOT/RST visible). Its silkscreen labels are on the underside, so pinout diagrams in datasheets are mirrored relative to the cell-table positions once the board is flipped over to mount it.

## Cell table

```
            1     2     3     4     5     6     7     8     9    10    11    12    13    14    15    16    17    18    19    20
   N      SLP   ▒▒▒   ▒▒▒   ▒▒▒   ▒▒▒   ▒▒▒   IN4     ·     ·     ·     ·     ·     ·     ·     ·     ·     ·     ·     ·     ·
   M     OUT1   ▒▒▒   ▒▒▒   ▒▒▒   ▒▒▒   ▒▒▒   IN3     ·     ·     ·     ·     ·     ·     ·     ·     ·     ·     ·     ·     ·
   L     OUT2   ▒▒▒   ▒▒▒   ▒▒▒   ▒▒▒   ▒▒▒   GND  104-     ★   47-     ·     ·     ·     ·     ·     ·     ·     ·     ·     ·
   K     OUT3   ▒▒▒   ▒▒▒   ▒▒▒   ▒▒▒   ▒▒▒   VCC  104+     ·   47+     ·     ·     ·     ·     ·     ·     ·     ·     ·     ·
   J     OUT4   ▒▒▒   ▒▒▒   ▒▒▒   ▒▒▒   ▒▒▒   IN2     ·     ·     ·     ·     ·   e5V    eG   e3V    e4    e3    e2    e1    e0
   I      FAU   ▒▒▒   ▒▒▒   ▒▒▒   ▒▒▒   ▒▒▒   IN1     ·     ·     ·     ·     ·   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓
   H        ·     ·     ·     ·     ·     ·     ·     ·     ·     ·     ·     ·   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓
   G      vi-   ░░░   ░░░   ░░░   ░░░   ░░░   ░░░   vo-     ·     ·     ·     ·   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓
   F      vi-   ░░░   ░░░   ░░░   ░░░   ░░░   ░░░   vo-     ·     ·     ·     ·   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓
   E        ·   ░░░   ░░░   ░░░   ░░░   ░░░   ░░░     ·     ·     ·   104   104   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓   ▓▓▓
   D        ·   ░░░   ░░░   ░░░   ░░░   ░░░   ░░░     ·     ·     ·     ·     ·    e5    e6    e7    e8    e9   e10   e20   e21
   C      vi+   ░░░   ░░░   ░░░   ░░░   ░░░   ░░░   vo+     ·     ·  470-  470+     ·     ·     ·     ·     ·     ·     ·     ·
   B      vi+   ░░░   ░░░   ░░░   ░░░   ░░░   ░░░   vo+     ·     ·     ·     ·     ·     ·     ·     ·     ·     ·     ·     ·
   A      PF1     ·   PF2     ·     ·     ·     ·     ·     ·     ·   GND    5V   Sig     ·     ·     ·     ·     ·     ·     ·

   BAT+ enters at the row-A left entrance pad, BAT− at the row-B left entrance pad.
   N20 motor wires solder directly to M1 (OUT1) and L1 (OUT2), twisted pair exits LEFT edge.
```

**Key.** `▓` `░` `▒` are cells under a module's PCB body (unreachable, leave unused). `★` at L9 = star ground junction. `e5V`/`eG`/`e3V`/`e0`…`e21` are ESP32 pin labels (`e` prefix). DRV `VCC` is the combined motor+logic supply. Cap labels carry polarity in the `+`/`−` suffix; `104` (ceramic) is non-polar. Buck-DRV gap row (row H cols 1–7) and buck-cap gap cols (cols 9–10) are intentionally empty for module-body clearance.

## Wiring

All jumpers go on the **back (solder) side** of the perfboard, hence modules sit on top with pin headers sticking down. The buck's paired pins (`vi+`×2, `vi-`×2, `vo+`×2, `vo-`×2) are the same net; jumper one to the other for extra current handling.

### Wire color key

One color per net so the back of the board stays traceable later. Substitute whatever's in your kit if you're missing a color.

| Color | Net | Gauge |
|---|---|---|
| **Red** | 5 V rail (buck Vo+ to all loads), `nSLEEP` tie | 22 AWG |
| **Yellow** | Battery rail (BAT+ → polyfuse → buck `vi+`) | 22 AWG |
| **Black** | GND, everything to star ★ at L9, including BAT− | 22 AWG |
| **Orange** | Servo PWM signal | 28–30 AWG |
| **Green** | DRV `IN1` | 28–30 AWG |
| **Blue** | DRV `IN2` | 28–30 AWG |

### Connections

| Net | Color | From | To |
|---|---|---|---|
| 5 V rail | red | C8 (vo+, paired with B8) | J13 (e5V), K7 (VCC), K8 (104+), K10 (47+), A12 (5V), C12 (470+), E12 (104) |
| nSLEEP tie | red | K7 (VCC) | N1 (SLP) |
| BAT+ in | yellow | row-A entrance pad | A3 (PF2), routed on the back side since A2 is under the polyfuse body |
| Post-fuse | yellow | A1 (PF1) | B1 / C1 (vi+ paired) |
| GND star | black | each its own wire to L9 (★) | L7 (DRV GND), L8 (104−), L10 (47−), J14 (eG), F8 / G8 (vo− paired), F1 / G1 (vi− paired), A11 (SG90 GND), C11 (470−), E11 (104) |
| BAT− in | black | row-B entrance pad | L9 (★) |
| Servo signal | orange | D13 (`e5` = GPIO5) | A13 (Sig), 3-cell jumper through empty B13 / C13 |
| Motor IN1 | green | J17 (`e3` = GPIO3) | I7 (IN1) |
| Motor IN2 | blue | J16 (`e4` = GPIO4) | J7 (IN2) |
| Motor leads | (any) | M1 (OUT1), L1 (OUT2) | N20 terminals (twisted pair, off-board, exits left edge) |

ESP32 strap pins to avoid driving at boot: GPIO2, GPIO8, GPIO9 (BOOT button). GPIO20/21 are default UART0, usable as GPIO if you don't need `Serial.print` over USB-CDC.

## Critical assembly notes

1. **Star ground at L9.** Every GND wire is its own run to ★, no daisy-chaining. The motor return current (~1.5 A peak) must not flow through the buck's feedback reference or the ESP32's GND, or it will modulate BLE.
2. **Antenna clearance.** The ESP32 chip antenna overhangs past col 20 at roughly rows F–G. Keep ≥2 cm of clearance from metal axles, screws, and motor cases. Plastic LEGO is RF-transparent and fine.
3. **Polyfuse direction.** PF2 (A3) is the battery side, PF1 (A1) is the load side. Route the BAT+ wire on the back of the board. Don't run it through A2 on the top.
4. **Cap polarity.** Stripe / short lead = negative. 470 µF: stripe to C11. 47 µF: stripe to L10. Reverse polarity = pop.
5. **Twisted motor pair.** Wires from M1 / L1 to the N20 are twisted ~1 turn/cm. The 100 nF cap across the N20 terminals on the motor body itself kills most of the brush noise. It's the single most important cap in the build.
6. **nSLEEP tie.** The DRV8833 stays asleep unless `nSLEEP` is HIGH. Short jumper from N1 to K7 (VCC) at assembly. If you ever want software sleep control, route to a spare GPIO instead.
7. **Buck pin pitch.** MP1584EN pin spacing isn't exactly 0.1". Bend each pin slightly outward at the perfboard surface before pushing the module down and don't force it.
8. **USB-C accessibility.** The connector overhangs the col-13 edge. That edge must be reachable from outside the chassis shell, otherwise you're lifting the perfboard out for every reflash.

## Power chain

```
2× 18650 (8.4 V fully charged) → reverse-polarity board → row-A entrance pad
                                                    │
                                                    ▼ back-side wire across row A
                                              A3 (PF2) ── polyfuse ── A1 (PF1)
                                                                          │
                                                                          ▼ 1-row jumper
                                                                    B1/C1 (vi+)
                                                                    MP1584EN buck
                                                                          │
                                                                          ▼ vo+ at B8/C8
                                                                      5 V rail
                                                                          │
                                                              ┌───────────┼──────────────┐
                                                              ▼           ▼              ▼
                                                       J13 (ESP32)  A12 (SG90)    K7 (DRV VCC)
                                                                                          │
                                                                                          ▼ OUT1/OUT2 at M1/L1
                                                                                       N20 motor
```

## N20 motor decoupling (off-board)

The most important cap in the entire build is the one at the motor: brushed DC motors radiate HF noise from arc-induced brush currents that escape down the wires before any board-level cap can shunt them. **Solder a 100 nF ceramic directly across the two N20 terminal tabs, on the motor body itself.**

*Optional*: the "every dB matters" RC/drone trick is to add two more 100 nF caps from each terminal to the motor case (scuff and tin a spot on the can, solder the cap leads). Skip it unless you actually see noise; the across-terminals cap alone is enough for normal use.

## SG90 servo notes

The 470 µF + 100 nF stack on the perfboard sits a couple rows above the SG90 connector, decoupling the servo as close to its connector as you can get without opening the case. If you ever see jitter at stall or rapid step changes: open the SG90 (4 small Phillips screws) and add a 10–22 µF ceramic across V+ / GND on its internal PCB, or add another small ceramic at the connector for higher-frequency content.
