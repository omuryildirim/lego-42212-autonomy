import argparse
import asyncio
import sys
import time

import serial
from serial import SerialException

# Try to import bleak for BLE support
try:
    import bleak
    BLEAK_AVAILABLE = True
except ImportError:
    BLEAK_AVAILABLE = False


def listen_serial(port: str, baud: int = 115200) -> int:
    """Read sensor snapshots from the USB serial port and print them."""
    try:
        ser = serial.Serial(port, baud, timeout=0.5)
    except SerialException as error:
        print(f"Error: could not open {port}: {error}")
        return 1

    # Give the board a moment after the port opens (USB-CDC re-enumerates).
    time.sleep(1.5)
    ser.reset_input_buffer()
    print(f"Listening on {port} @ {baud} baud. Press Ctrl+C to stop.")

    try:
        while True:
            line = ser.readline()
            if line:
                sys.stdout.write(line.decode("utf-8", errors="replace"))
                sys.stdout.flush()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        ser.close()
    return 0


async def listen_ble() -> int:
    """Subscribe to the BLE TX characteristic and print sensor snapshots."""
    if not BLEAK_AVAILABLE:
        print("Error: bleak library required for BLE mode")
        print("Install with: pip install bleak")
        return 1

    # Nordic UART TX characteristic — the firmware notifies snapshots here.
    TX_CHAR_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

    print("Scanning for LEGO-42212...")
    devices = await bleak.BleakScanner.discover()
    target = None
    for device in devices:
        if device.name and "LEGO-42212" in device.name:
            target = device
            break

    if not target:
        print("LEGO-42212 not found. Available devices:")
        for device in devices:
            if device.name:
                print(f"  - {device.name}")
        return 1

    print(f"Found LEGO-42212 at {target.address}")

    def on_notify(_characteristic, data: bytearray):
        sys.stdout.write(data.decode("utf-8", errors="replace"))
        sys.stdout.flush()

    async with bleak.BleakClient(target.address) as client:
        print("Connected. Subscribing to sensor stream. Press Ctrl+C to stop.")
        await client.start_notify(TX_CHAR_UUID, on_notify)
        try:
            while client.is_connected:
                await asyncio.sleep(1.0)
        except KeyboardInterrupt:
            print("\nStopped.")
        finally:
            try:
                await client.stop_notify(TX_CHAR_UUID)
            except Exception:
                pass
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Listen to sensor snapshots from the LEGO 42212 ESP32-C3"
    )
    parser.add_argument("--mode", choices=["serial", "ble"], default="serial",
                        help="Listen mode: 'serial' for USB, 'ble' for Bluetooth")
    parser.add_argument("--port", help="Serial port (required for serial mode), e.g., COM4")
    parser.add_argument("--baud", type=int, default=115200, help="Serial baud rate (default: 115200)")
    args = parser.parse_args()

    if args.mode == "serial":
        if not args.port:
            print("Error: --port required for serial mode (e.g., --port COM4)")
            return 1
        return listen_serial(args.port, args.baud)
    return asyncio.run(listen_ble())


if __name__ == "__main__":
    sys.exit(main())
