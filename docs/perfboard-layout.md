# Perfboard layout (40×60 mm motherboard)

Single-board "motherboard" that integrates the ESP32-C3 SuperMini, MP1584EN buck, DRV8833, polyfuse, decoupling caps, and the SG90 servo connector. The reverse-polarity protection module mounts separately on the chassis (it has no solder pads).

Board: 40×60 mm perfboard, 20 columns × 14 rows (labelled `1`–`20` along one edge, `A`–`N` along the other), each hole isolated, with ~12 larger entrance pads along each short edge (left and right). Row labels are printed bottom-to-top on the physical perfboard, so **row A is at the bottom and row N is at the top** — the cell table below is drawn the same way.

This layout uses two entrance pads on the left edge (rows A, B for BAT+/BAT−). The remaining ~22 pads are unused — keep them in reserve for future expansion (encoder wires, IMU I²C, UART debug, or multimeter test points for the 5 V / 3.3 V / GND rails).

## Decoupling cap inventory

| Role | Part | Polarity |
|---|---|---|
| N20 across motor terminals | 100 nF ceramic (`104`) | no |
| N20 case caps (optional delta filter, ×2) | 100 nF ceramic (`104`) | no |
| SG90 bulk on perfboard | 470 µF / 16 V electrolytic | yes — stripe to GND |
| SG90 ceramic in parallel | 100 nF ceramic (`104`) | no |
| DRV8833 VCC bulk | 47 µF / 25 V electrolytic | yes — stripe to GND |
| DRV8833 VCC ceramic in parallel | 100 nF ceramic (`104`) | no |

Voltage rationale: caps on the 5 V rail need ≥10 V rating. The DRV8833 VCC bulk cap is on the 5 V rail (since this DRV8833 module variant has a single VCC pin that powers both motor and logic — no separate battery tap), so 25 V is comfortable over-spec. Use whatever you have on hand; 10 V or 16 V is fine. Ceramic code `104` = 10 × 10⁴ pF = 100 nF (0.1 µF).

## Topology

```
   ◄── motor wires (M1/L1) and BAT+/− all exit the LEFT edge ──►

         col 1                                                col 20
   row N  ┌──────────────┐
          │  DRV8833     │  (7 cols × 6 rows, pins at col 1 & col 7)
          │  (vertical,  │
          │   OUT ◄ │    │
          │   IN  ▶ )    │
   row I  └──────────────┘  ──────  ESP32 body at cols 13–20  ──────►
   row J  ── DRV row J ────────  ESP32 top pin row (5V/GND/3V3/GPIO0–4) at J13–J20
   row H  ── buck-DRV gap row at cols 1–7 ──────────────  ESP32 body  ──────►
   row G  ┌──────────────────┐                ┌────────────────────────────┐
          │   MP1584EN buck  │                │  ESP32-C3 SuperMini        │
          │  (horizontal,    │                │  (horizontal, 90° CCW,     │
          │   IN ◄ │ OUT ▶)  │                │   power row at row J,      │
   row B  └──────────────────┘                │   GPIO row at row D)       │
          [polyfuse A1─A3]                    │  USB-C ◄ col 13 side       │
   row A                                      │  antenna ▶ off right edge  │
                                  [SG90]      └────────────────────────────┘
                                  cols
                                  11–13
```

The DRV8833 sits at the top-left (cols 1–7, rows I–N — 7 holes wide), buck directly below at rows B–G with row H as a free gap between them — this gives the buck module's top edge clearance over the perfboard guideline. Both modules face their OUT-edges toward the centre and their IN-edges to the left, so all high-current connections (motor wires, BAT+/−) exit the left edge of the board. The ESP32 lies horizontally on the right half (cols 13–20, rows D–J), rotated 90° CCW from the original vertical orientation. With components face-up and the rotation, the 5 V and GND pins land near the centre column (J13 / J14), and `GPIO5` at D13 sits three cells above the SG90 signal pin at A13 for a near-direct servo signal connection (bridges through empty B13 / C13). USB-C now points left (out the col-13 edge of the ESP32 footprint, well clear of the 470 µF cap that sits on row C) and the chip antenna overhangs past col 20 off the right edge of the perfboard — opposite corner from the motor noise.

This DRV8833 module variant (12 pins: `IN4/IN3/GND/VCC/IN2/IN1` on one side, `SLEEP/OUT1/OUT2/OUT3/OUT4/FAULT` on the other) has a single `VCC` pin that powers both motor and logic — there's no separate battery tap. The buck's 5 V output feeds VCC, ESP32 5V, and SG90 5V through one shared rail. The motor runs at 5 V instead of battery voltage; you lose a bit of N20 top-end speed but gain a much simpler power topology and the chip's 5.5 V max VCC limit is respected automatically.

## Zone allocation

| Zone | Cols | Rows | Notes |
|---|---|---|---|
| DRV8833 (vertical, 90° CCW) | 1–7 | I–N | 7 holes wide. OUT side on col 1 (left edge), IN side on col 7 (centre-facing). Body covers cols 2–6 |
| DRV8833 100 nF ceramic | 8 | K–L | leads at K8 (+) and L8 (−) — one col right of DRV `VCC`/`GND` at K7/L7 |
| Star GND ★ | 9 | L | central junction next to both cap negatives |
| DRV8833 47 µF bulk | 10 | K–L | leads at K10 (+) and L10 (−) — across ★ from the 104, ceramic closest to the IC |
| Buck (MP1584EN) (horizontal, 90° CCW) | 1–8 | B–G | IN side on col 1 (left edge), OUT side on col 8 (centre-facing). Body covers cols 2–7 |
| Buck-DRV gap row | 1–7 | H | intentionally empty — gives the buck module's top edge clearance from the DRV8833 |
| Polyfuse | 1–3 | A | 3-cell span on row A (leads at A1 and A3, body bridges A2). PF1 is the load-side lead (1-row jumper to buck `vi+`); PF2 is the battery-side lead (BAT+ wire enters here) |
| Buck-cap gap cols | 9–10 | A–C | intentionally empty — separates the bulky 470 µF cap from the buck Vo+ pin |
| SG90 cluster | 11–13 | A, C, E | 3-pin connector on row A (cable exits bottom edge); 470 µF on row C (leads at C11/C12); 100 nF on row E (leads at E11/E12) — caps spaced apart so they don't crowd each other or the ESP32 bottom pin row |
| ESP32-C3 SuperMini | 13–20 | D–J | horizontal mount, components face up; rotated 90° CCW so the power side (5V/GND/3V3/GPIO0–4) lands on row J and the GPIO side (GPIO5–21) on row D; USB-C overhangs col 13, antenna overhangs past col 20 (off the right edge of the perfboard) |
| Free area | 4–10 (row A), 9–20 (row B), 13–20 (row C), 11–12 (rows F–G), 8–12 (row J), 8–20 (rows K–N rest) | varies | available for routing back-side jumpers, future expansion |

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

   Left edge entrance pads:
     row A (col 0) — BAT+ in (jumpered across row A to PF2 at A3)
     row B (col 0) — BAT- in (jumpered to ★ star GND at L9)
   Motor wires:
     M1 (OUT1) and L1 (OUT2) — solder N20 motor pair directly to these pads, twist along the run, exits LEFT edge
```

`▓` `░` `▒` cells: module body sits *above* the perfboard on its pin headers — those holes are physically unreachable once the module is mounted, leave unused.

## Legend

| Label | Position | Function |
|---|---|---|
| `e5V` | J13 | ESP32 5 V (Vin) — feed from buck Vo+ |
| `eG`  | J14 | ESP32 GND (single pin on the SuperMini) |
| `e3V` | J15 | ESP32 3.3 V output (not needed by this DRV8833 — VCC alone powers logic + motor) |
| `e4`–`e0` | J16→J20 | GPIO4, GPIO3, GPIO2, GPIO1, GPIO0 (also ADC1 channels) |
| `e5`–`e10` | D13→D18 | GPIO5, GPIO6, GPIO7, GPIO8, GPIO9, GPIO10 |
| `e20` `e21` | D19, D20 | GPIO20 (RX), GPIO21 (TX) — usable as GPIO if you don't need UART debug |
| `vo+` `vo-` | C8/B8, G8/F8 | Buck VOUT+ / VOUT− (5 V output, paired pins for current) |
| `vi+` `vi-` | C1/B1, G1/F1 | Buck VIN+ / VIN− (battery rail input, paired pins) |
| `SLP` | N1 | DRV8833 nSLEEP — must be tied HIGH (to VCC) for normal operation |
| `OUT1` `OUT2` | M1, L1 | DRV8833 motor A outputs → N20 motor wires (exit left edge) |
| `OUT3` `OUT4` | K1, J1 | DRV8833 motor B outputs (unused — channel B not connected) |
| `FAU` | I1 | DRV8833 nFAULT — leave floating, or wire to a GPIO for fault detection |
| `IN1` | I7 | DRV8833 motor A direction 1 ← chosen ESP32 GPIO |
| `IN2` | J7 | DRV8833 motor A direction 2 ← chosen ESP32 GPIO |
| `VCC` | K7 | DRV8833 motor + logic supply (single rail, fed from buck 5 V) |
| `GND` | L7 | DRV8833 ground |
| `IN3` `IN4` | M7, N7 | DRV8833 motor B inputs (unused) — tie LOW to GND or leave floating |
| `104+/-` | K8, L8 | 100 nF ceramic on DRV VCC — closest cap to the IC for HF transients |
| `47+/-` | K10, L10 | 47 µF / 25 V electrolytic on DRV VCC bulk — stripe to `47-` |
| `GND` `5V` `Sig` | A11, A12, A13 | SG90 3-pin connector (brown / red / orange) |
| `470+/-` | C12, C11 | 470 µF / 16 V electrolytic (servo bulk) — stripe to `470-` (over GND) |
| `104` (×2 in E) | E11, E12 | 100 nF ceramic in parallel with the 470 µF (one row clear of the ESP32 bottom pins on row D) |
| `PF1` `PF2` | A1, A3 | Polyfuse — leads bent across 3-col span on row A (body bridges A2). PF1 is the load side (short 1-row jumper to buck `vi+`); PF2 is the battery side (BAT+ wire enters here) |
| `★` | L9 | Star GND junction |

DRV8833 specific pin order varies by module — verify against your silkscreen before committing. The order shown above matches the 12-pin variant where one side has `IN4/IN3/GND/VCC/IN2/IN1` and the other has `SLEEP/OUT1/OUT2/OUT3/OUT4/FAULT`, rotated 90° CCW so that OUT pins end up on the left col and IN pins on the right col of the DRV's 7-cell-wide footprint.

ESP32-C3 SuperMini pin order assumes the board is mounted **components face up** (chip antenna, USB-C, BOOT/RST visible from above). The silkscreen labels are on the bottom (solder) side, so what you see in pinout images is mirrored relative to how the pins actually land on the perfboard once the module is flipped over to mount it.

When picking GPIOs in firmware:
- **Servo signal — fix at GPIO5.** Layout-locked: D13 (`e5`) sits three cells above A13 (Sig), with B13 / C13 empty between them — a single short jumper handles this connection.
- **Motor IN1/IN2 — pick from row J (ESP32 top pin row).** Row J sits directly above the DRV's `IN1`/`IN2` pins on row I/J, so the wires run mostly along a single row instead of crossing the board. GPIO3 at J17 → I7 (`IN1`) is ~11 cells; GPIO4 at J16 → J7 (`IN2`) is a straight ~9-cell hop along row J. GPIO6/7/10 on row D also work but require crossing 5+ rows. Avoid GPIO2 (J18 — strap pin), GPIO8/GPIO9 (also strap, GPIO9 is the BOOT button). GPIO20/21 are the default UART0 pins; usable as GPIO if you don't need serial debug, but you'll lose `Serial.print` over USB-CDC if you reassign them.

## Wiring list

All routes use insulated jumper wire on the **back (solder) side** of the perfboard — modules sit on the component side, their pin headers stick down through into your jumper space underneath. Top side stays clear for module bodies and air clearance. The buck's paired pins (`vi+`×2, `vi-`×2, `vo+`×2, `vo-`×2) bond to the same net — solder one wire to either pin of the pair, or bridge them with a short jumper for current-handling.

### Wire color key

Pick one color per net and stick to it. The scheme below follows standard hobbyist conventions; substitute whatever's in your kit if you're missing one, just keep "one net = one color" so you can trace the back side at a glance later.

| Color | Net |
|---|---|
| **Red** | 5 V rail (post-buck) — every wire carrying regulated 5 V, including the `nSLEEP` tie-up to VCC. 22 AWG. |
| **Yellow** | Battery rail (pre-buck) — BAT+ entry, through the polyfuse, to buck `vi+`. Raw battery voltage, ~7.4 V. 22 AWG. (Orange would be the textbook choice but orange 22 AWG is rare; yellow is the common substitute and reads as "caution / unfused".) |
| **Black** | GND — every wire to the star point at L9, including BAT−. 22 AWG. |
| **Orange** | Servo PWM signal (`e5` → SG90 Sig). 28–30 AWG. Matches the orange signal wire on the SG90 stock cable. |
| **Green** | DRV8833 `IN1` (motor direction 1). 28–30 AWG. |
| **Blue** | DRV8833 `IN2` (motor direction 2). 28–30 AWG. |

The N20 motor leads (off-board, soldered to M1/L1) aren't jumpers — use whatever pair came with the motor or any matched pair you have, just twist them together along the run.

### Connections

| Net | Color | From | To |
|---|---|---|---|
| 5 V rail (post-buck) | red | C8 (vo+ paired with B8) | J13 (e5V), K7 (VCC), K8 (104+), K10 (47+), A12 (5V), C12 (470+), E12 (104) |
| nSLEEP tie-up | red | K7 (VCC) | N1 (SLP) — short jumper, keeps DRV8833 awake |
| BAT+ in (pre-fuse) | yellow | left entrance pad row A | A3 (PF2) — runs across row A on the back side (A2 is under the polyfuse body, so don't route the wire through A2 on the top) |
| Battery rail (post-fuse) | yellow | A1 (PF1) | B1/C1 (vi+ paired) — short 1-row jumper |
| Star GND ★ (at L9) | black | each its own wire | L7 (DRV GND), L8 (104-), L10 (47-), J14 (eG), F8/G8 (vo- paired), F1/G1 (vi- paired), A11 (SG90 GND), C11 (470-), E11 (104) |
| BAT− in | black | left entrance pad row B | L9 (★) |
| Servo signal | orange | D13 (`e5` = GPIO5) | A13 (Sig) — 3-cell jumper through empty B13 / C13 |
| Motor control IN1 | green | J17 (`e3` = GPIO3) | I7 (IN1) — runs along row J, drops one row at col 7 (~11 cells) |
| Motor control IN2 | blue | J16 (`e4` = GPIO4) | J7 (IN2) — straight along row J (~9 cells) |
| Motor wires (to N20) | (motor pair) | M1 (OUT1), L1 (OUT2) | solder motor pair directly, twist along the run, exits LEFT edge col 1 |

Wire gauges:
- High-current GND (DRV8833, BAT−, buck): 22 AWG.
- Battery rail to buck Vi+: 22 AWG.
- 5 V rail (buck Vo+ to all loads): 22 AWG — DRV8833 motor current goes through this rail now.
- Signal lines (servo, IN1/IN2): 28–30 AWG is fine. (The servo signal hop D13→A13 is short enough you can use a bent leg trimmed off a resistor instead of a wire.)

### Why star ground (and not daisy-chain)

In star topology every load's GND wire converges at one point (`★` at L9). BAT−, the buck's `vi-`/`vo-`, DRV8833 GND, ESP32 `eG`, all the cap negatives, and the SG90 GND each get their own wire to `★`. The motor return current (peak ~1.5 A at N20 stall) flows from DRV GND straight to `★` to BAT−, isolated from the buck's feedback reference and the ESP32's GND.

The alternative is daisy-chained / linear: BAT− → buck input GND → buck output GND → loads. It's less wiring and works fine in steady state — vi− and vo− are the same node inside the buck anyway. But under pulsed motor current, the chain develops small voltage drops that show up at the buck's feedback divider (regulation noise) and at the ESP32's GND reference (BLE jitter). Star avoids that by giving each load its own clean return.

## Assembly principles

1. **Star ground.** All GND points get their own wire to the single star point at `L9`. Do *not* daisy-chain — motor return current must not flow through the ESP32's ground reference, or it will create ground bounce that the BLE radio sees.
2. **Antenna overhang.** With the ESP32 rotated 90° CCW and pushed to the right edge, the chip antenna physically overhangs past col 20 (off the right edge of the perfboard) at roughly rows F–G. This is ideal for BLE range — no copper anywhere near the antenna. Don't run any wires under that area, and keep the back side of cols 19–20 rows F–G free of solder bridges or jumper crossings.
3. **Decoupling caps go at the load.** Caps live as close as possible to the pins they're feeding — DRV ceramic at K8/L8 sits one col right of `VCC`/`GND` at K7/L7 (closest to the IC for HF transients); the 47 µF bulk sits two cols further right at K10/L10 across the star, since bulk caps are tolerant of a small extra trace length. SG90 caps stack vertically: 470 µF bulk right above the connector at C11/C12, 100 nF one row clear at E11/E12 (skipping row D where the ESP32 GPIO row is).
4. **Twisted motor pair.** The two wires from `OUT1` (M1) and `OUT2` (L1) to the N20 motor should be twisted together along their full run. Twisted pair cancels radiated noise.
5. **Cap polarity.** On every electrolytic, the stripe / short lead is the negative terminal. Stripe → GND, long lead → V+. The 470 µF on row C straddles GND (col 11) and 5 V (col 12): stripe to C11 (`470-`), long lead to C12 (`470+`). The 47 µF on row K/L straddles VCC (col 10 row K) and GND (col 10 row L): stripe to L10 (`47-`), long lead to K10 (`47+`). Reverse polarity = the cap fails, sometimes spectacularly.
6. **Buck pin spacing.** The MP1584EN module's pin spacing isn't a clean 0.1". Bend each pin slightly inward at the perfboard surface before pushing the module down — don't force.
7. **Module orientation.** All three modules (ESP32, buck, DRV8833) mount components-face up — chip antenna, USB-C connector, BOOT/RST buttons visible from above. On the ESP32-C3 SuperMini the silkscreen pin labels are on the *bottom* (solder) side, so they're hidden once mounted. The cell table reflects the components-up view: pin labels you see in datasheet images are mirrored left-to-right when you flip the board over to mount it. Solder header pins so the long side hangs down through the perfboard, plastic spacer rests against the upper face.
8. **Socket the ESP32, solder the rest.** Use stackable male-female pin headers (or female socket strips) on the perfboard at the ESP32 zone (rows D and J, cols 13–20) so the ESP32 SuperMini can lift out without desoldering. Pop it out for USB-C programming (no power conflict between USB VBUS and buck 5 V), or to swap modules during firmware bring-up. Direct-solder the buck and DRV8833 — those don't need to come out, and the DRV8833's motor current is happier through a soldered joint than a friction-fit socket contact.
9. **nSLEEP tie-up.** The DRV8833 stays in low-power sleep unless `nSLEEP` is HIGH. Tie N1 (SLP) to K7 (VCC) with a short jumper at assembly. If you ever want software-controlled sleep, replace this jumper with a wire to a spare GPIO instead.
10. **Long 5 V wire.** The buck output at C8/B8 is ~12 cells from the ESP32 5 V pin at J13 (about 30 mm of back-side routing) and ~9 cells from DRV `VCC` at K7 (about 23 mm). Use 22 AWG for both — they carry the combined ESP32 + SG90 + DRV8833 motor current (peak ~1.5 A at N20 stall).
11. **Buck-DRV gap row (H).** Row H at cols 1–7 is intentionally left empty so the MP1584EN module's top edge has clearance over the perfboard's printed guideline before the DRV8833 starts at row I. At cols 13–20, row H is the ESP32 body — that part stays populated.
12. **Buck-cap gap cols (9–10).** Cols 9–10 at rows A–C are intentionally left empty so the bulky 470 µF cap at C11/C12 doesn't crowd the buck's `vo+`/`vo-` pin column. The cap is a radial electrolytic ~8 mm in diameter — its body extends ~1 cell in each direction from its lead pair, so this 2-col gap keeps it clear of the buck while still letting it sit close enough to the SG90 connector for low-impedance decoupling.
13. **USB-C clearance.** With the ESP32 at rows D–J, the USB-C connector sits at roughly rows F–G on the col-13 side — three rows above the 470 µF cap on row C. That gives the USB-C plug body and cable boot vertical clearance over the cap when you're plugging in for programming.
14. **Polyfuse direction.** PF2 (A3) is the BAT+ entry side — the BAT+ wire from the entrance pad on row A col 0 routes across the back side to A3 (don't run it through A2 on the top side; that cell is under the polyfuse body). PF1 (A1) is the load side — short 1-row jumper from A1 down to B1 (buck `vi+`). This puts the long pre-fuse wire on the dangerous side (raw battery, harder to spot a wiring mistake from the perfboard edge inward) and the short post-fuse jumper on the protected side. Reversing this is fine electrically (the polyfuse is symmetric) but loses the labeling convention and the easy visual check of "the long row-A trace = unfused".

## Mounting to LEGO

Neither side of the populated perfboard is flat enough for double-sided foam tape — the bottom side has solder joints and pin tails, the top side has module bodies. Two practical options:

- **Standoffs through corner holes.** Use M2 or M2.5 hex spacers (~5–10 mm tall) screwed through the perfboard's four corner holes (or drill new corner holes if your board doesn't have them). Mount the standoffs to a 3D-printed Technic-compatible plate — a flat plate with 4.8 mm Technic pin-holes spaced on an 8 mm grid, drilled to take the standoff screws. The plate clips into the chassis with standard Technic pegs. This is the cleanest option and matches how the existing 3D-printed motor/servo couplers attach.
- **Zip ties to a Technic frame.** Run zip ties through unused perfboard holes and around a Technic beam underneath. Faster to build, less rigid — fine for bench testing or first drives, less ideal once the car is moving fast and vibrating.

The 3D-printed plate is the better long-term answer; a starter `.stl` belongs in `docs/3d-printing/` once the perfboard layout is fully validated.

## N20 motor decoupling (off-board, at the motor itself)

The most important capacitor in the whole build is the one *at the motor*, not on the perfboard. Brushed DC motors radiate noise from arc-induced HF currents that escape down the wires before any board-level cap can shunt them.

**Minimum** — solder a 100 nF ceramic directly across the two N20 terminal tabs, on the motor body itself. Not at the DRV8833 end.

```
                   100 nF ceramic
                   ┌─────┤├─────┐
                   │            │
                   │            │
       ────────────┴── T1   T2 ─┴────────────
                       ┌─────────┐
                       │   N20   │      ← cap soldered to the
                       │  motor  │        terminal tabs here
                       └─────────┘
                       │         │
                  to OUT1      to OUT2
                    on perfboard
```

**Best** (full delta filter) — add two more 100 nF ceramics from each terminal to the motor case (the metal can). Lightly scuff a spot on the can, tin it, and solder the cap leads. The case becomes a local HF return path for brush noise.

```
                     ┌─────┤├─────┐
                     │    100 nF  │
                     │            │
        ─────────────┴── T1   T2 ─┴─────────────
                         │         │
                         │         │
                       ┤├          ┤├
                       100 nF    100 nF
                         │         │
                         └────┬────┘
                              │
                         motor case
                       (metal body)
```

If only the across-terminals cap is fitted, the build still works fine; the case caps are the "every dB matters" version used in RC and drone work.

## SG90 servo decoupling notes

The 470 µF on the perfboard sits one row above the SG90 connector (C11 above A11 = GND, C12 above A12 = 5V), separated from the servo's internal motor only by the unavoidable ~10 cm stock lead. This is the cleanest placement short of opening the servo case. The 100 nF ceramic at E11/E12 is two more rows up — close enough to handle HF transients but clear of the ESP32 bottom pin row on row D.

If you ever see jitter at stall or rapid step changes, options to improve:
- Open the SG90 (4 small Phillips screws) and add a 10–22 µF ceramic across V+/GND on its internal PCB.
- Add a small ceramic in parallel right at the connector for higher-frequency content.

The 100 nF ceramic in parallel with the 470 µF (E11/E12) handles the fast transient edges that the bulk electrolytic is too slow for.

## Power chain summary

```
   2× 18650 (~7.4 V nominal, 8.4 V peak)
        │
        ▼
   reverse-polarity board   ── mounted separately on chassis
        │
        ▼
   BAT+ wire to perfboard left entrance pad (row A)
        │
        ▼ across row A (back side; A2 is under polyfuse body)
   A3 (PF2) ── polyfuse ── A1 (PF1)
        │
        ▼ short 1-row jumper
   B1/C1 (vi+)
   MP1584EN buck
        ↓ vo+ at B8/C8
        5 V rail
        │
        ├─→ ESP32 e5V at J13
        ├─→ SG90 5V at A12
        └─→ DRV8833 VCC at K7
            ↓ OUT1/OUT2 at M1/L1
            N20 motor (twisted pair, exits left edge)
```

Note the difference from the original architecture: this DRV8833 module has only one power pin (VCC) that supplies both motor and logic, so there's no separate battery rail tap to the chip. The motor runs at 5 V rather than 7.4 V; you give up some peak speed but gain a simpler topology and stay under the chip's 5.5 V max VCC.
