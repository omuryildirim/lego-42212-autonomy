# BLE control

The firmware exposes a Nordic-UART-style BLE service so any BLE-capable device (PC, phone, BLE gamepad) can drive the car wirelessly. The Python keyboard bridge in [tools/keyboard_control.py](../tools/keyboard_control.py) is the easiest client.

## Enable / disable interfaces

Both interfaces live behind flags in [src/config.h](../src/config.h):

```cpp
#define ENABLE_SERIAL_INTERFACE 0   // USB serial commands
#define ENABLE_BLE_INTERFACE    1   // BLE wireless commands
```

Set either or both to `1`. They coexist cleanly — running with both lets you swap between cabled debug and wireless drive without reflashing.

## BLE profile

The ESP32-C3 advertises as `LEGO-42212` and runs as a GATT peripheral with a Nordic-UART-compatible service:

| | Value |
|---|---|
| Device name | `LEGO-42212` |
| Service UUID | `6e400001-b5a3-f393-e0a9-e50e24dcca9e` |
| RX characteristic (write) | `6e400002-b5a3-f393-e0a9-e50e24dcca9e` |
| TX characteristic (notify) | `6e400003-b5a3-f393-e0a9-e50e24dcca9e` |

Clients write ASCII commands to the RX characteristic.

## Command grammar

Same for BLE and serial. Newline-terminated, ASCII:

```
drive <throttle -1..1> <steering -1..1>
throttle <value -1..1>
steering <value -1..1>
stop
help
```

Examples: `drive 0.5 0.0`, `drive 0.7 -0.3`, `stop`.

A 500 ms watchdog stops the car if no command arrives — applies to both transports.

## Drive it from your PC

```bash
pip install -r tools/requirements.txt
python tools/keyboard_control.py --mode ble
```

The script scans for `LEGO-42212` and connects automatically. Controls: **W/A/S/D** or arrow keys, **Space** = emergency stop.

## Drive it from a generic BLE client

Any GATT client works — useful for debugging:

- **nRF Connect for Desktop** ([download](https://www.nordicsemi.com/Products/Development-tools/nRF-Connect-for-Desktop)) — connect to `LEGO-42212`, write ASCII bytes to the RX characteristic.
- **LightBlue** or **Bluefruit Connect** on iOS / Android — same idea from a phone.

## Latency

Roughly 20–100 ms per BLE write vs. 1–10 ms for USB serial. Both are well within the 500 ms watchdog and feel fine for manual driving.

## Troubleshooting

**Device doesn't show up in scans** — confirm `ENABLE_BLE_INTERFACE 1`, reflash, then power-cycle the ESP32. Sanity-check with nRF Connect; if it sees `LEGO-42212` the firmware is fine and the issue is on the client side.

**Script can't connect** — on Windows, allow BLE under Settings → Privacy → Bluetooth. Move closer to the ESP32. Check the script's "available devices" list (printed when no match is found).

**Connection drops** — typical at 10–30 m range or behind walls. The ESP32 re-advertises automatically; reconnect.

**Commands seem to do nothing** — verify it works over USB serial first to rule out hardware. Then re-check pins, the polyfuse, and battery state.
