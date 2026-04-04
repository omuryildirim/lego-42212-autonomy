# BLE Control Setup

This document explains the new BLE (Bluetooth Low Energy) feature and how to use it to wirelessly control the LEGO car.

## Architecture Overview

The firmware now supports both Serial USB and BLE communication interfaces. You can enable or disable each interface independently.

### Files Added

1. **[src/config.h](../src/config.h)**: Central configuration
   - `ENABLE_SERIAL_INTERFACE`: 1 to enable USB serial, 0 to disable
   - `ENABLE_BLE_INTERFACE`: 1 to enable BLE, 0 to disable
   - BLE UUIDs (standard UART-like UUIDs for broad compatibility)

2. **[src/serial_interface.h/cpp](../src/serial_interface.h)**: 
   - Handles all USB serial command input
   - Can coexist with BLE

3. **[src/ble_interface.h/cpp](../src/ble_interface.h)**:
   - Implements BLE GATT server (peripheral)
   - Advertises as "LEGO-42212"
   - Accepts commands via BLE characteristic writes

### Modified Files

- **[src/main.cpp](../src/main.cpp)**:
  - Removed serial-specific command reading
  - Both interfaces initialize in setup()
  - Both interfaces update in loop()
  - Motor/servo control logic unchanged

## Configuration Options

### Use Serial Only
For USB cable-based control:

```cpp
// In src/config.h
#define ENABLE_SERIAL_INTERFACE 1
#define ENABLE_BLE_INTERFACE 0
```

Then use the keyboard_control.py with `--mode serial`.

### Use BLE Only
For wireless control:

```cpp
// In src/config.h
#define ENABLE_SERIAL_INTERFACE 0
#define ENABLE_BLE_INTERFACE 1
```

Then use the keyboard_control.py with `--mode ble`.

### Use Both
For simultaneous USB and wireless:

```cpp
// In src/config.h
#define ENABLE_SERIAL_INTERFACE 1
#define ENABLE_BLE_INTERFACE 1
```

You can then run keyboard_control.py in either mode.

## BLE Command Format

The BLE interface uses the same command format as serial:

```
drive <throttle -1..1> <steering -1..1>
throttle <value -1..1>
steering <value -1..1>
stop
help
```

Examples:
```
drive 0.5 0.0
drive 0.7 -0.3
stop
throttle 0.8
```

## How BLE Works (Technical)

The ESP32-C3 acts as a **GATT server (peripheral)** with:

1. **Service UUID**: `6e400001-b5a3-f393-e0a9-e50e24dcca9e` (Nordic UART Service)
2. **RX Characteristic**: `6e400002-b5a3-f393-e0a9-e50e24dcca9e` (write from client to ESP32)
3. **TX Characteristic**: `6e400003-b5a3-f393-e0a9-e50e24dcca9e` (read/notify from ESP32 to client)

The device advertises as "LEGO-42212" and is discoverable by any BLE-capable device.

## Using the Python Keyboard Bridge with BLE

The keyboard_control.py script now supports both serial and BLE modes:

```powershell
# Serial mode (USB connected)
python tools/keyboard_control.py --mode serial --port COM3

# BLE mode (wireless)
python tools/keyboard_control.py --mode ble
```

In BLE mode, the script will automatically scan for and connect to "LEGO-42212".

### Controls

- `W` or `Up`: forward
- `S` or `Down`: reverse
- `A` or `Left`: steer left
- `D` or `Right`: steer right
- `Space`: emergency stop / neutral

## Alternative Control Methods

You can also control via:

1. **nRF Connect Desktop** (advanced BLE debugging)
   - Available from: https://www.nordicsemi.com/Products/Development-tools/nRF-Connect-for-Desktop
   - Connect to "LEGO-42212" service UUID `6e400001-...`
   - Write commands directly to RX characteristic `6e400002-...`

2. **LightBlue** or **Bluefruit Connect** apps (mobile)
   - Available on iOS, Android
   - Scan for "LEGO-42212"
   - Send commands to the service

## Testing Checklist

**Before using BLE for the first time:**

- [ ] Update config.h to enable BLE
- [ ] Build and flash firmware
- [ ] Ensure keyboard_control.py has Bleak installed: `pip install bleak`
- [ ] Run: `python tools/keyboard_control.py --mode ble`
- [ ] Script should find and connect to "LEGO-42212"
- [ ] Press W key to move forward
- [ ] Press A/D to steer
- [ ] Press Space to stop
- [ ] Verify motor and servo respond

## Troubleshooting

### ESP32 does not appear in scan

1. Check that firmware was uploaded successfully
2. Check that `ENABLE_BLE_INTERFACE 1` in config.h
3. Power cycle the ESP32 (USB disconnect/reconnect)
4. Check serial monitor if also running serial monitor

### Script cannot find device

1. Verify the device is advertising: Use nRF Connect Desktop as a test
2. Check that "LEGO-42212" is visible in BLE scan
3. Move closer to the ESP32
4. Power cycle the ESP32 and retry scan

### Commands do not execute

1. First test with USB serial to confirm motor works
2. Then switch to BLE and retest
3. Check that polyfuse and battery are connected
4. Verify GPIO pins are correct in main.cpp

### Connection drops

1. This is normal if you move too far away (BLE range is ~10-30 meters typically)
2. The ESP32 will re-advertise after disconnection
3. Reconnect and resume sending commands

## Performance Notes

- BLE latency: typically 20-100ms per command
- USB serial latency: typically 1-10ms per command
- Both are acceptable for this car prototype
- 500ms command timeout safety still applies to BLE

## Quick Reference

| Feature | Value |
|---------|-------|
| Device Name | LEGO-42212 |
| Service UUID | 6e400001-b5a3-f393-e0a9-e50e24dcca9e |
| RX Characteristic | 6e400002-b5a3-f393-e0a9-e50e24dcca9e |
| TX Characteristic | 6e400003-b5a3-f393-e0a9-e50e24dcca9e |
| Command Format | Same for both Serial and BLE |
| Timeout Safety | 500ms (same for both) |

## Side-by-Side Comparison

### Serial (USB)

Pros:
- Lower latency
- More stable connection

Cons:
- Tethered by cable

### BLE (Wireless)

Pros:
- No cable
- Mobile device compatible
- Long range (10-30m)

Cons:
- Slightly higher latency

You can use both at the same time by setting both enable flags to 1.
