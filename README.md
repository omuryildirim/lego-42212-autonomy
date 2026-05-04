# Autonomous electrified LEGO 42212

Electrify LEGO Technic set [#42212](https://www.lego.com/sv-se/product/ferrari-fxx-k-42212) with an ESP32-C3, a single drive motor, and a steering servo. Control it from a PC over BLE or USB. Roadmap: full self-driving autonomy.

![Finished build](docs/images/car-hero.jpg)
*Image coming soon — finished car on the bench.*

## What this is

- **Now** — a minimal, low-cost retrofit of LEGO #42212 with one drive motor, one steering servo, and wireless control from a PC.
- **Next** — onboard sensing and perception to make the car autonomous.
- **Constraint** — every part is chosen for price/performance. Stock hobby-grade modules, no exotic hardware.

![Driving demo](docs/images/car-driving.gif)
*GIF coming soon — first drive.*

## Prerequisites

- **VS Code** with the **PlatformIO IDE** extension — for building and flashing the firmware.
- **Python 3.9+** — for the desktop keyboard bridge.
- **A PC with Bluetooth Low Energy** (most laptops from the last ~5 years) — only for BLE mode.
- **Git** — to clone this repo.
- The hardware listed in the [Bill of materials](#bill-of-materials) below, plus a USB-C cable to flash the ESP32-C3.

## Quick start

1. Wire the hardware. Work through the bench-test docs in [docs/](docs/) before assembling on the chassis.
2. Open this folder in VS Code with the PlatformIO extension. Default board is `esp32-c3-devkitm-1`; change it in [platformio.ini](platformio.ini) if yours differs.
3. Build and flash. Replace the port with whatever your OS assigns to the ESP32-C3 (Windows: `COM3`, macOS: `/dev/cu.usbmodem*`, Linux: `/dev/ttyACM0` or `/dev/ttyUSB0`).

   Windows (PowerShell):

   ```powershell
   & "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run -t upload --upload-port COM3
   ```

   macOS / Linux:

   ```bash
   ~/.platformio/penv/bin/platformio run -t upload --upload-port /dev/ttyACM0
   ```

   If `platformio` (or `pio`) is on your `PATH`, just run `pio run -t upload --upload-port <port>`.

4. Drive it. Two options — they coexist; pick one (or enable both in [src/config.h](src/config.h)):

   **Wireless (BLE)** — enabled by default. Install Python deps, then run the keyboard bridge:

   ```bash
   pip install -r tools/requirements.txt
   python tools/keyboard_control.py --mode ble
   ```

   **USB serial** — set `ENABLE_SERIAL_INTERFACE 1` in [src/config.h](src/config.h), reflash, then:

   ```bash
   python tools/keyboard_control.py --mode serial --port <your-port>
   ```

   Controls: **W/A/S/D** or arrow keys, **Space** for emergency stop. Full BLE setup in [docs/ble-setup.md](docs/ble-setup.md).

## Hardware

![Components](docs/images/components.jpg)
*Image coming soon — all parts laid out before assembly.*

### Bill of materials

| Component | Purpose | Approx. price (USD) |
|---|---|---|
| ESP32-C3 DevKitM-1 | MCU + BLE radio | €2–3 |
| GA12-N20 micro gear motor | Rear-axle drive | €1–2 |
| SG90 micro servo (or MG90, EMax ES08) | Steering | €1–2 |
| DRV8833 motor driver module | H-bridge for the N20 | €1–3 |
| MP1584EN buck converter | 5 V rail for ESP32 and servo | €1–2 |
| 5–26 V reverse-polarity protection board | Battery input safety | €1–2 |
| 4 A 30 V resettable polyfuse | Short-circuit protection | <€1 |
| 2× 18650 Li-ion cells + holder | Power source (~7.4 V nominal) | €6–16 |
| 2× ceramic capacitors (~100 nF) | Motor brush noise suppression | <€0.50 |

### Tools and consumables

| Item | Purpose |
|---|---|
| Breadboard | Bench-testing each subsystem before integration |
| Perfboard or small PCB | Final compact wiring |
| Soldering iron + solder | Headers, modules, motor leads |
| Heat-shrink tubing | Insulating splices |
| Zip ties + double-sided tape | Mechanical attachment to the LEGO chassis |
| Multimeter | Voltage and continuity checks before connecting the battery |

Prices are typical AliExpress and hobby-electronics ranges. In my experience you can get a better deals especially with AliExpress.

## Design decisions

**ESP32-C3 over ESP32 / ESP32-S3.** Cheaper (~€3 vs. €5–8), single-core RISC-V is plenty for one motor and one servo, and built-in USB-serial saves an external UART chip. The tradeoff: the C3 supports BLE only — no Bluetooth Classic — so it cannot pair with PS or Xbox gamepads. It can still talk to any modern PC, phone, or BLE-native gamepad, which is enough for now.

**N20 + DRV8833 for drive.** N20 gear motors are the smallest credible drive option that fits inside a Technic chassis. The DRV8833 is the cheapest dual H-bridge that handles the N20's stall current (~1.5 A) without a heatsink. Two 100 nF capacitors across the motor terminals kill brush noise that would otherwise reset the ESP32.

**SG90 for steering.** A standard SG90 (or any MG90/ES08-class equivalent) is the lightest servo at this price point. Steering force on a LEGO chassis is tiny, so torque is not the limiter.

**MP1584EN buck for the 5 V rail.** Two 18650s in series sit at 6.4–8.4 V — too high for the SG90 and the ESP32, fine for the motor through the DRV8833. The MP1584EN regulates the logic, motor driver and servo rail to a clean 5 V.

**Reverse-polarity board + polyfuse.** Lithium cells deliver enough current to destroy parts on a wiring mistake. The protection board guards against polarity flips during assembly; the 4 A polyfuse trips on a short. Combined cost is under €3 — cheap insurance. Of course you can get protected 18650 batteries, e.g. XTAR, Nitecore etc., but that makes the batteries physically longer and naturally more expensive. So I prefered to buy unprotected batteries and implement an effortless basic protection myself.

## More documentation

Bench tests (run in this order before integrating on the chassis):

1. [Servo bench test](docs/servo-breadboard-setup.md) — first SG90 check on USB-C power.
2. [N20 + DRV8833 bench test](docs/n20-breadboard-setup.md) — first motor drive on USB-C power.
3. [Buck converter bench test](docs/buck-breadboard-setup.md) — verify 5 V regulation before connecting 18650s.

Control software:

- [docs/ble-setup.md](docs/ble-setup.md) — wireless setup, BLE UUIDs, command grammar.
- [tools/README.md](tools/README.md) — desktop keyboard bridge.

Mechanical:

- [docs/3d-printing/README.md](docs/3d-printing/README.md) — printable couplers for SG90, EMax ES08MA II, and GA12-N20 to LEGO Technic axles. I used [jlcpcb.com](https://jlcpcb.com) for printing, and I can only recommend them if you don't have access to 3D printers (or your local 3D printing alternatives are really expensive). Their shipping is pretty fast and they provide bunch of coupons for new customers. You can order couple of samples for every part this repository has under €3-5.

![Motor placement](docs/images/motor-placement.jpg)
*Image coming soon — N20 and SG90 mounted in the chassis.*

![3D-printed adapters](docs/images/3d-print-adapters.jpg)
*Image coming soon — printed couplers joining motor and servo shafts to LEGO axles.*

## Roadmap

- [x] Manual drive over USB serial
- [x] Manual drive over BLE
- [ ] Onboard IMU and wheel encoders
- [ ] Camera + companion compute (Pi / Jetson) for perception
- [ ] Closed-loop autonomous driving

## Project layout

```
src/
  main.cpp              motor + steering control loop
  config.h              feature flags, BLE UUIDs
  serial_interface.*    USB serial command parser
  ble_interface.*       BLE GATT server
tools/
  keyboard_control.py   desktop keyboard bridge (serial or BLE)
docs/                   wiring, bench tests, BLE setup, 3D prints
platformio.ini          PlatformIO env + libraries
```
