# LEGO 42212 ESP32-C3 drive prototype

This repository contains a minimal ESP32 firmware starting point for a LEGO 42212 drive prototype with:

- Host-computer keyboard input over USB serial
- One GA-N20 DC motor through a DRV8833
- One SG90 servo for steering
- ESP32-C3 firmware built with PlatformIO in VS Code

## Why this stack

The implementation uses C++ with the Arduino framework on ESP32 because it keeps the first version simple while still giving access to mature PWM and serial support. The first control path is deliberately split in two:

- The ESP32-C3 only handles low-level motor and steering control.
- The laptop handles Bluetooth and keyboard input, then sends normalized commands over USB serial.

That is a better fit for the ESP32-C3 than direct PS5 or keyboard Bluetooth handling, and it gives you a clean migration path to Raspberry Pi later.

## Project layout

- `platformio.ini`: PlatformIO environment and library dependencies
- `src/main.cpp`: Serial-controlled motor and steering control for ESP32-C3
- `tools/keyboard_control.py`: Optional desktop keyboard bridge that sends commands over serial
- `docs/`: Wiring and bring-up notes

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

- Start with [docs/servo-breadboard-setup.md](d:\Projects\autonomous-lego-42212\docs\servo-breadboard-setup.md) for the first SG90 bench test over USB-C power.
- Continue with [docs/n20-breadboard-setup.md](d:\Projects\autonomous-lego-42212\docs\n20-breadboard-setup.md) for the first DRV8833 + N20 bench test over USB-C power.