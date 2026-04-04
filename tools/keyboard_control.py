import argparse
import asyncio
import sys
import time

import pygame
import serial
from serial import SerialException
from serial import SerialTimeoutException

# Try to import bleak for BLE support
try:
    import bleak
    BLEAK_AVAILABLE = True
except ImportError:
    BLEAK_AVAILABLE = False


def compute_axis(positive_pressed: bool, negative_pressed: bool) -> float:
    if positive_pressed and not negative_pressed:
        return 1.0
    if negative_pressed and not positive_pressed:
        return -1.0
    return 0.0


class SerialController:
    def __init__(self, port: str, baud: int = 115200):
        self.serial_port = serial.Serial(port, baud, timeout=0.1, write_timeout=0.05)
        time.sleep(1.5)
        self.serial_port.reset_input_buffer()
        self.serial_port.reset_output_buffer()
        self.connected = True

    async def send_command(self, command: str) -> str:
        try:
            self.serial_port.write(command.encode("ascii"))
            return "connected"
        except (SerialException, SerialTimeoutException) as error:
            self.connected = False
            return f"serial error: {error}"

    def close(self):
        try:
            self.serial_port.close()
        except:
            pass


class BLEController:
    def __init__(self):
        self.client = None
        self.connected = False
        self.device_address = None
        # Standard Nordic UART UUIDs
        self.SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
        self.RX_CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"

    async def connect(self) -> bool:
        """Find and connect to LEGO-42212 device"""
        try:
            print("Scanning for LEGO-42212...")
            devices = await bleak.BleakScanner.discover()
            
            target_device = None
            for device in devices:
                if device.name and "LEGO-42212" in device.name:
                    target_device = device
                    break
            
            if not target_device:
                print("LEGO-42212 not found. Available devices:")
                for device in devices:
                    if device.name:
                        print(f"  - {device.name}")
                return False
            
            print(f"Found LEGO-42212 at {target_device.address}")
            self.device_address = target_device.address
            self.client = bleak.BleakClient(target_device.address)
            await self.client.connect()
            self.connected = True
            print("Connected to LEGO-42212")
            return True
        except Exception as error:
            print(f"BLE connection error: {error}")
            return False

    async def send_command(self, command: str) -> str:
        """Send command via BLE"""
        if not self.connected or not self.client:
            return "not connected"
        
        try:
            await self.client.write_gatt_char(self.RX_CHAR_UUID, command.encode("ascii"))
            return "connected"
        except Exception as error:
            self.connected = False
            return f"ble error: {error}"

    async def close(self):
        if self.client and self.connected:
            try:
                await self.client.disconnect()
            except:
                pass
            self.connected = False


async def main_async(mode: str, port: str = None, baud: int = 115200) -> int:
    if mode == "serial":
        if not port:
            print("Error: --port required for serial mode")
            return 1
        controller = SerialController(port, baud)
    elif mode == "ble":
        if not BLEAK_AVAILABLE:
            print("Error: bleak library required for BLE mode")
            print("Install with: pip install bleak")
            return 1
        controller = BLEController()
        if not await controller.connect():
            return 1
    else:
        print(f"Error: Unknown mode '{mode}'. Use 'serial' or 'ble'")
        return 1

    pygame.init()
    pygame.display.set_caption("LEGO 42212 Keyboard Control")
    pygame.display.set_mode((520, 180))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 22)

    throttle = 0.0
    steering = 0.0
    running = True
    last_sent = 0.0
    status = "connected"
    send_interval = 1.0 / 20.0  # 20 Hz command rate

    print("Keyboard bridge started")
    print("Controls: W/S or Up/Down for throttle, A/D or Left/Right for steering, Space to stop")

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_SPACE]:
                throttle = 0.0
                steering = 0.0
            else:
                throttle = compute_axis(
                    pressed[pygame.K_w] or pressed[pygame.K_UP],
                    pressed[pygame.K_s] or pressed[pygame.K_DOWN],
                )
                steering = compute_axis(
                    pressed[pygame.K_d] or pressed[pygame.K_RIGHT],
                    pressed[pygame.K_a] or pressed[pygame.K_LEFT],
                )

            now = time.monotonic()
            if now - last_sent >= send_interval:
                command = f"drive {throttle:.2f} {steering:.2f}\n"
                status = await controller.send_command(command)
                last_sent = now

            surface = pygame.display.get_surface()
            surface.fill((22, 22, 22))
            lines = [
                f"LEGO 42212 keyboard control ({mode.upper()})",
                "W/S or Up/Down: throttle",
                "A/D or Left/Right: steering",
                f"throttle={throttle:+.2f} steering={steering:+.2f}",
                status,
                "Space: stop   Close window: exit",
            ]

            for index, line in enumerate(lines):
                text = font.render(line, True, (235, 235, 235))
                surface.blit(text, (20, 20 + index * 28))

            pygame.display.flip()
            clock.tick(60)
    finally:
        try:
            await controller.send_command("stop\n")
        except Exception:
            pass
        
        if isinstance(controller, BLEController):
            await controller.close()
        else:
            controller.close()
        
        pygame.quit()

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Keyboard bridge for LEGO 42212 ESP32-C3 controller")
    parser.add_argument("--mode", choices=["serial", "ble"], default="serial", 
                        help="Control mode: 'serial' for USB, 'ble' for Bluetooth")
    parser.add_argument("--port", help="Serial port (required for serial mode), e.g., COM5")
    parser.add_argument("--baud", type=int, default=115200, help="Serial baud rate (default: 115200)")
    args = parser.parse_args()

    # Run async main
    return asyncio.run(main_async(args.mode, args.port, args.baud))


if __name__ == "__main__":
    sys.exit(main())