import argparse
import sys
import time

import pygame
import serial
from serial import SerialException
from serial import SerialTimeoutException


def compute_axis(positive_pressed: bool, negative_pressed: bool) -> float:
    if positive_pressed and not negative_pressed:
        return 1.0
    if negative_pressed and not positive_pressed:
        return -1.0
    return 0.0


def send_command(serial_port: serial.Serial, command: str) -> str:
    try:
        serial_port.write(command.encode("ascii"))
        return "connected"
    except (SerialException, SerialTimeoutException) as error:
        return f"serial error: {error}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Keyboard bridge for LEGO 42212 ESP32-C3 controller")
    parser.add_argument("--port", required=True, help="Serial port, for example COM5")
    parser.add_argument("--baud", type=int, default=115200, help="Serial baud rate")
    parser.add_argument("--rate", type=float, default=20.0, help="Command send rate in Hz")
    args = parser.parse_args()

    interval = 1.0 / args.rate
    serial_port = serial.Serial(args.port, args.baud, timeout=0.1, write_timeout=0.05)
    time.sleep(1.5)
    serial_port.reset_input_buffer()
    serial_port.reset_output_buffer()

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
            if now - last_sent >= interval:
                status = send_command(serial_port, f"drive {throttle:.2f} {steering:.2f}\n")
                last_sent = now

            surface = pygame.display.get_surface()
            surface.fill((22, 22, 22))
            lines = [
                "LEGO 42212 keyboard control",
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
            send_command(serial_port, "stop\n")
        except SerialException:
            pass
        serial_port.close()
        pygame.quit()

    return 0


if __name__ == "__main__":
    sys.exit(main())