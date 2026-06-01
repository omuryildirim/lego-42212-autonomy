# Sensors bench test (VL53L8 ToF + MPU-9265 IMU)

Read both sensors over I2C and stream a snapshot table over USB serial and BLE every 500 ms. No motor drive in this mode — the DRV8833 inputs are held low so the buck rail can stay connected without anything moving.

## You need

- ESP32-C3 SuperMini (loose on a breadboard, or the assembled perfboard with the 18650 pack disconnected)
- USB-C cable to the laptop
- MPU-9265 breakout (any MPU-9250-pin-compatible board works)
- SATEL-VL53L8 satellite breakout
- Breadboard and jumper wires
- Two ~4.7 kΩ I2C pull-ups to 3V3 (most MPU breakouts already have them; check before adding more)

## Pins and wires

Both sensors share one I2C bus. SDA and SCL each fan out from a single ESP32 pin to **both** sensor breakouts in parallel — easiest on a breadboard is to drop a short jumper from the ESP32 pin to a free rail column, then run one wire from that column to each sensor. Default 7-bit addresses don't collide: MPU-9265 at `0x68`, VL53L8 at `0x29`.

### Wire-by-wire

One row per physical wire. 13 wires total: 5 to the MPU, 8 to the SATEL.

| # | From (ESP32-C3) | To | Net |
|---|---|---|---|
| 1 | 3V3 | MPU `VCC` | 3.3 V |
| 2 | GND | MPU `GND` | GND |
| 3 | GPIO 6 | MPU `SDA` | I2C SDA |
| 4 | GPIO 7 | MPU `SCL` | I2C SCL |
| 5 | GND | MPU `AD0` | sets address `0x68` (skip if breakout ties AD0 low on board) |
| 6 | **5V / VBUS** | SATEL `5VO` | **5 V** — board power input (see note below) |
| 7 | GND | SATEL `GND` | GND |
| 8 | GPIO 6 | SATEL `SDA` (`MOSI_SDA`) | I2C SDA (same net as wire 3) |
| 9 | GPIO 7 | SATEL `SCL` (`MCLK_SCL`) | I2C SCL (same net as wire 4) |
| 10 | GPIO 10 | SATEL `LPn` | ToF enable |
| 11 | 3V3 | SATEL `PWREN` | enables the onboard regulators (logic enable, not a supply) |
| 12 | GND | SATEL `SPI_I2C_N` | selects I2C mode (must be low) |
| 13 | 3V3 | SATEL `NCS` | tie high for I2C mode |

Wires 3 and 8 are the same I2C-SDA net; wires 4 and 9 are the same I2C-SCL net. Tie them at a breadboard column rather than running two long wires from the ESP32.

> **Power the SATEL from 5 V, not 3.3 V.** The SATEL-VL53L8 carries its own LDOs that generate the sensor's three internal rails (AVDD 3.3 V, IOVDD, CORE 1.8 V) from a single **5 V input on `5VO`**, gated by `PWREN`. The header pins labelled `1V8`, `3V3`, and `IOVDD` are regulator **outputs / test points — leave them unconnected.** Do *not* feed 3.3 V into them (that back-feeds an LDO output) and do *not* expect 3.3 V on `PWREN` alone to power the board — `PWREN` is only an enable. With no 5 V on `5VO`, the chip never powers up and NACKs at `0x29`. The ESP32-C3 SuperMini exposes 5 V on its `5V`/`VBUS` pad while USB is connected.

### What lands where on the perfboard

GPIO 6 / 7 break out at perfboard pads `D14` / `D15`, GPIO 10 at `D18`, 3V3 at `J15`, GND at `J14`. The MPU sits on the perfboard at row N (pads N10–N20); the SATEL stays off-board on the breadboard with flying leads back to those same pads.

### Pins you can ignore on the SATEL

`I2C_RST` and `INT` can be left floating for this test — the firmware uses polled reads. Everything else above is required: `5VO` (power), `PWREN`, `SPI_I2C_N`, and `NCS` must all be wired or the chip won't appear on the bus.

## Procedure

1. Wire as above. Check 3V3, 5V, and GND with a multimeter before plugging either sensor in.
2. Build and flash. PlatformIO will pull `stm32duino/STM32duino VL53L8CX` on first build — the ~80 KB firmware blob lives in flash and takes a couple seconds to upload to the sensor on every boot.
3. Open the USB serial monitor at 115200 baud, **or** connect a BLE central to `LEGO-42212` and subscribe to the TX characteristic. Same payload goes to both.

## Expected

Boot log:

```
LEGO 42212 sensor bench
MPU WHO_AM_I=0x71
MPU ready: yes
ToF ready: yes
Streaming sensor snapshots
```

Then every 500 ms:

```
==================== Sensors @ 12345ms ====================
IMU  ax=+0.012 ay=-0.034 az=+0.998 g
     gx=  -0.21 gy=  +0.45 gz=  -0.18 dps   T=24.3C
ToF (mm, 4x4):
       123   145   167   189
       211   233   255   277
       299   321   343   365
       387   409   431   453
============================================================
```

Sanity checks:

- Lay the IMU flat: `az ≈ +1.000`, `ax`/`ay ≈ 0`. Flip it: `az ≈ -1.000`.
- Wave a hand 10 cm above the ToF: matching zones drop to ~100 mm; uncovered zones stay at the ceiling distance.
- Rotate the board around one axis: `gx`/`gy`/`gz` reads the corresponding rate, near zero when still.

## If it misbehaves

The `ToF offline` line in the stream carries its own diagnosis: the step that failed, the status code, and a live probe of the sensor's I2C address, e.g. `ToF  offline (failed at init_sensor, status=255, 0x29 NACK)`.

- **`MPU: WHO_AM_I read failed`** — pull-ups missing, SDA/SCL swapped, or 3V3 not present at the MPU.
- **`MPU WHO_AM_I=0xFF`** — open bus. Push the jumpers back in.
- **`ToF  offline ... 0x29 NACK`** — the sensor isn't on the bus at all. Almost always power or mode-select on the SATEL: no 5 V on `5VO` (the most common mistake — `PWREN` tied to 3V3 only *enables* the regulators, it doesn't power them), `SPI_I2C_N` not pulled low (board stuck in SPI mode), `NCS` not tied high, or `LPn`/GPIO 10 not actually reaching the board. The MPU answering on the same SDA/SCL proves the bus itself is fine, so isolate to the SATEL.
- **`ToF  offline ... 0x29 ACK` but `failed at init_sensor`** — chip is powered and addressable but the firmware-blob upload failed. Usually the I2C clock is too fast for your flying-lead wiring; `kI2cClockHz` is already dropped to `100000` in [src/main.cpp](../src/main.cpp). Shorten the leads or power-cycle.
- **`ToF  no new frame` forever** — `start_ranging` succeeded but no frame ever lands. Power-cycle (the firmware blob upload occasionally hangs the chip after a partial init).
- **All ToF cells read `0` or `65535`** — sensor looking at no target / out of range. Place a hand at ~20 cm.
- **ESP32-C3 resets at boot** — the VL53L8 inrush can dip the rail on USB power if your laptop's port is weak. Try a different port or add a 10 µF ceramic across the SATEL board's 5V/GND pins.

## Where things go on the perfboard

The MPU sits on the perfboard at the row-N strip above the DRV8833 (pads N10–N20). Three wires reach it from the ESP32 pads:

- `J15` (3V3) → MPU VCC
- `J14` (GND) → MPU GND
- `D14` (GPIO 6) → MPU SDA, `D15` (GPIO 7) → MPU SCL

The VL53L8 stays off-board for now and connects through breadboard jumpers: the shared `D14`/`D15` (GPIO 6/7) SDA/SCL and `J14` (GND), plus `D18` (GPIO 10) for LPn. Note its supply is **5 V on `5VO`**, not the 3V3 `J15` net the MPU uses — source 5 V from the ESP32 `5V`/`VBUS` pad (confirm which perfboard pad carries VBUS before wiring). It also needs `PWREN`→3V3, `SPI_I2C_N`→GND, and `NCS`→3V3 as described above.
