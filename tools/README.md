# Running Keyboard Control Script

From the project root, run:
```bash
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r tools/requirements.txt
```

Then start the bridge with your board’s COM port:
```bash
python tools/keyboard_control.py --port COM5
```

If you are unsure about the port number, then find the correct port first:
```bash
.\.venv\Scripts\python.exe -m serial.tools.list_ports -v
```

If multiple ports are listed:
```bash
# run once with the board unplugged
.\.venv\Scripts\python.exe -m serial.tools.list_ports -v

# connect the board and run again
.\.venv\Scripts\python.exe -m serial.tools.list_ports -v
```

Use the new port that appears after connecting the board.

> [!NOTE]  
> You can also use PlatformIO to find the device list:
> ```bash
> & "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" device list
> ```

Then run the bridge with the detected port:
```bash
python tools/keyboard_control.py --port COM7
```

