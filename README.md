# LEGO 42212 ESP32-C3 drive prototype

This repository contains a minimal ESP32 firmware starting point for a LEGO 42212 drive prototype with:

- Host-computer keyboard input over USB serial
- One GA-N20 DC motor through a DRV8833
- One SG90 servo for steering
- ESP32-C3 firmware built with PlatformIO in VS Code

## Why this stack

The implementation uses C++ with the Arduino framework on ESP32 because it keeps the first version simple while still giving access to mature PWM and Serial/BLE support. The control paths are deliberately split in two:

- The ESP32-C3 only handles low-level motor and steering control.
- The host (laptop or phone) handles input and sends normalized commands via USB serial or BLE.

That is a better fit for the ESP32-C3 than direct PS5 or keyboard Bluetooth handling, and it gives you a clean migration path to Raspberry Pi later.

## Control options

You can control the car via:

1. **USB Serial + Keyboard Bridge** (default, wired): Connect via USB cable and use the included Python keyboard bridge
   - See [tools/README.md](./tools/README.md) for setup
   - Lower latency, most reliable

2. **Wireless BLE**: Connect any BLE-capable device (phone, laptop with Bluetooth)
   - See [docs/ble-setup.md](./docs/ble-setup.md) for instructions
   - No cable required, mobile-friendly

You can use both at the same time by editing [src/config.h](./src/config.h).

## Project layout

- `platformio.ini`: PlatformIO environment and library dependencies
- `src/main.cpp`: Motor and steering control (works with Serial or BLE)
- `src/config.h`: Feature flags to enable/disable Serial or BLE
- `src/serial_interface.h/cpp`: Serial (USB) communication handler
- `src/ble_interface.h/cpp`: BLE (wireless) communication handler
- `tools/keyboard_control.py`: Optional desktop keyboard bridge for Serial mode
- `docs/`: Wiring, bring-up notes, and control setup guides

## 3D printing adapters

The repository also includes printable adapters for coupling common hobby motors and servos to Lego Technic axle-compatible parts:

- EMax ES08MA II mini servo to Lego axle adapter
- SG90 mini servo to Lego axle adapter
- GA12-N20 micro metal gear motor to Lego axle adapter

See [docs/3d-printing/README.md](./docs/3d-printing/README.md) for the available models and part notes.

## Default keyboard mapping

- `W` or `Up`: forward
- `S` or `Down`: reverse
- `A` or `Left`: steer left
- `D` or `Right`: steer right
- `Space`: emergency stop / neutral

The desktop helper sends `drive <throttle> <steering>` commands at a fixed rate. The firmware stops the car if commands stop arriving for 500 ms.

## Pin assumptions

Update the pins in `src/main.cpp` if your ESP32-C3 board or wiring differs.

- GPIO 4 -> DRV8833 IN1
- GPIO 5 -> DRV8833 IN2
- GPIO 6 -> SG90 signal

## Wiring notes

- Keep the ESP32-C3, DRV8833, servo, and power regulators on a shared ground.
- Do not power the SG90 directly from an ESP32-C3 GPIO pin; the signal line is separate from servo power.
- Be careful with motor voltage. Many GA-N20 motors are rated for 3V to 6V. A 2-cell 18650 pack is 8.4V when fully charged, which can overdrive the motor if you feed the DRV8833 motor supply directly from the battery pack.
- If your motor is a 6V variant, regulate the motor supply to a safe voltage before the DRV8833 motor supply input.
- Servo current spikes can reset the ESP32-C3 if the 5V rail is weak or noisy. If that happens, improve decoupling and power distribution before changing software.

## Serial protocol

The firmware accepts newline-terminated commands at 115200 baud:

- `drive <throttle -1..1> <steering -1..1>`
- `throttle <value -1..1>`
- `steering <value -1..1>`
- `stop`
- `help`

Examples:

```text
drive 0.60 0.00
drive 0.40 -0.50
stop
```

## Build and flash

1. Install PlatformIO in VS Code.
2. Open this folder in VS Code.
3. If your board is not an `esp32-c3-devkitm-1`, change the board in `platformio.ini`.
4. Build and flash with PlatformIO.

If `platformio` is not on your shell PATH, the default Windows CLI location is usually `C:\Users\<your-user>\.platformio\penv\Scripts\platformio.exe`.

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run -t upload --upload-port COM3
````

To monitor ESP32 runtime, connect to ESP32 via serial port:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" device monitor --port COM3 --baud 115200
````

## Desktop keyboard bridge

1. Install Python 3 on your computer.
2. Install desktop dependencies:

```powershell
pip install -r tools/requirements.txt
```

3. Flash the ESP32-C3 firmware.
4. Find the board COM port in Device Manager or the PlatformIO device list.
5. Run the keyboard bridge:

```powershell
python tools/keyboard_control.py --port COM5
```

Your Bluetooth keyboard stays paired to the computer, not to the ESP32-C3.

## Next steps

- Add a dedicated configuration header for pin assignments and steering limits.
- Add steering centering and throttle calibration values.
- Replace the Python keyboard bridge with a Raspberry Pi or laptop gamepad bridge later.

## Wiring docs

- Start with [docs/servo-breadboard-setup.md](./docs/servo-breadboard-setup.md) for the first SG90 bench test over USB-C power.
- Continue with [docs/n20-breadboard-setup.md](./docs/n20-breadboard-setup.md) for the first DRV8833 + N20 bench test over USB-C power.
- Continue with [docs/buck-breadboard-setup.md](./docs/buck-breadboard-setup.md) for a safe first buck-converter bench check over USB-C power before the 18650 step.