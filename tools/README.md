# Running Keyboard Control Script

## Installation

From the project root, run:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r tools/requirements.txt
```

## Usage

The keyboard_control.py script supports both **Serial (USB)** and **BLE (Wireless)** modes.

### Serial Mode (USB Connected)

First, find your ESP32-C3's COM port:

```powershell
# Method 1: Using serial tools
.\.venv\Scripts\python.exe -m serial.tools.list_ports -v

# Method 2: Using PlatformIO
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" device list
```

If multiple ports are listed, run before and after connecting the board to identify which port is new.

Then start the keyboard bridge:

```powershell
python tools/keyboard_control.py --mode serial --port COM3
```

Replace `COM3` with your actual port number.

### BLE Mode (Wireless)

Make sure your ESP32-C3 has BLE enabled in [src/config.h](../src/config.h):

```cpp
#define ENABLE_BLE_INTERFACE 1
```

Then start the keyboard bridge in BLE mode:

```powershell
python tools/keyboard_control.py --mode ble
```

The script will automatically scan for and connect to "LEGO-42212".

## Default Keyboard Mapping

Once running, use these keys to control the car:

- **W** or **Up Arrow**: Forward
- **S** or **Down Arrow**: Reverse
- **A** or **Left Arrow**: Steer left
- **D** or **Right Arrow**: Steer right
- **Space**: Emergency stop / neutral
- **Close Window**: Exit

## Troubleshooting

### Serial mode: COM port not found

1. Check that ESP32-C3 is connected via USB-C
2. Try different ports if multiple are listed
3. Verify [src/config.h](../src/config.h) has `ENABLE_SERIAL_INTERFACE 1`

### BLE mode: Device not found

1. Verify ESP32-C3 has `ENABLE_BLE_INTERFACE 1` in config
2. Power cycle the ESP32-C3 (disconnect/reconnect USB)
3. Check that bleak is installed: `pip install bleak`
4. Ensure your computer has Bluetooth enabled

### BLE imports error

If you get `ImportError: No module named 'bleak'`, install it:

```powershell
pip install bleak
```

## Firmware Notes

Before running either mode, ensure the firmware is compiled and flashed:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run -t upload --upload-port COM3
```

For dual-mode operation, you can enable both interfaces in [src/config.h](../src/config.h):

```cpp
#define ENABLE_SERIAL_INTERFACE 1
#define ENABLE_BLE_INTERFACE 1
```

This allows you to run the keyboard bridge in either mode and control the same car.

