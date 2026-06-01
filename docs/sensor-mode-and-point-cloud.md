# Sensor mode & point cloud

The firmware has a second build-time personality: instead of driving the car it
can stream the **MPU-9265 IMU** and **VL53L8CX 8×8 Time-of-Flight** sensor over
USB serial and BLE. Two host-side tools consume that stream — a plain text
listener and a live 3D point-cloud visualizer that fuses the IMU to accumulate
geometry over time.

For wiring the two sensors to the ESP32-C3, see
[sensor-breadboard-setup.md](sensor-breadboard-setup.md). This doc covers the
firmware mode and the software side.

## Enabling sensor mode

The mode is selected by a flag in [src/config.h](../src/config.h):

```cpp
// 0 = car control (default), 1 = sensor bench
#define ENABLE_SENSOR_MODE 0
```

- `0` (default): car control — the motor + steering servo respond to drive
  commands. See [ble-setup.md](ble-setup.md).
- `1`: sensor bench — stream IMU + ToF snapshots; the motor outputs are held
  inert.

Set it to `1`, then build and flash:

```powershell
& "$env:USERPROFILE\.platformio\penv\Scripts\platformio.exe" run -t upload --upload-port COM4
```

The two modes live in separate translation units guarded by the flag
([car_control.cpp](../src/car_control.cpp), [sensor_bench.cpp](../src/sensor_bench.cpp))
behind a shared `Mode::setup()`/`Mode::loop()` interface ([mode.h](../src/mode.h)),
so only the selected mode is compiled in. Both serial and BLE are available in
either mode.

## Snapshot stream format

In sensor mode the firmware emits one snapshot every 100 ms (10 Hz) to **both**
USB serial and the BLE TX characteristic. The payload is identical on both
transports:

```
==================== Sensors @ 11046ms ====================
IMU  ax=+0.054 ay=+0.046 az=+1.034 g
     gx=  +3.54 gy=  -1.10 gz=  -0.87 dps   T=31.3C
ToF (mm, 8x8):
      1729  1737  1747  1752  1751  1773  1749  1750
      1728  1736  1746  1750  1758  1772  1763  1771
      1745  1740  1753  1764  1768  1763  1771  1786
      1745  1735  1756  1774  1771  1774  1763  1769
      1721  1690  1710  1764  1762  1779  1752  1766
      1714  1692  1708  1748  1772  1765  1770  1757
      1721  1729  1713  1752  1750  1751  1740  1741
      1712  1715  1737  1727  1741  1753  1752  1704
============================================================
```

- **Timestamp** — milliseconds since boot.
- **IMU** — accel in g (±2 g range), gyro in deg/s (±250 dps), die temperature.
- **ToF** — 8×8 grid of per-zone distances in mm (`0` / very large = no target or
  out of range).

When the ToF fails to initialize, the grid is replaced by a self-diagnosing
line, e.g. `ToF  offline (failed at init_sensor, status=255, 0x29 NACK)` — see
the troubleshooting section of [sensor-breadboard-setup.md](sensor-breadboard-setup.md).

The rate (10 Hz) is chosen to match the ToF's 8×8 ranging cap and to keep a
full ~680-byte snapshot within the 115200-baud serial budget while giving the
host enough IMU samples for gyro integration.

## Reading the stream — `sensor_listen.py`

Prints snapshots as they arrive. Useful for a quick sanity check.

```powershell
# Serial (USB) — close any other program holding the port first
python tools/sensor_listen.py --mode serial --port COM4

# BLE (wireless)
python tools/sensor_listen.py --mode ble
```

Flags: `--mode {serial,ble}`, `--port COMx` (serial), `--baud` (default 115200).

## Point cloud — `pointcloud.py`

Turns the stream into a live 3D point cloud, with IMU-based orientation tracking
and accumulation over time.

```powershell
python tools/pointcloud.py --mode serial --port COM4
```

### What it does

1. **Projection.** Each of the 64 ToF zones looks out along a slightly different
   angle within the sensor's ~45°×45° field of view (5.625° per zone in 8×8).
   Each distance is projected through its zone angle into a 3D point
   (`x`=right, `y`=up, `z`=forward).
2. **Orientation.** A complementary filter fuses the IMU: the accelerometer
   anchors absolute roll/pitch from gravity, and the gyro tracks fast motion and
   integrates yaw. Live roll/pitch/yaw is shown on screen.
3. **Accumulation.** Each frame is rotated into a gravity-aligned world frame and
   merged into a voxel grid, so panning/tilting the sensor builds up a denser
   cloud than any single 8×8 frame (current frame in orange; accumulated points
   colored faintly by height).

### Controls

| Key | Action |
|---|---|
| `r` | Reset the accumulated cloud and orientation |
| `a` | Toggle accumulation on/off |
| `space` | Pause/resume |

### Flags

| Flag | Default | Purpose |
|---|---|---|
| `--mode {serial,ble}` | `serial` | Transport |
| `--port COMx` | — | Serial port (serial mode) |
| `--baud` | `115200` | Serial baud |
| `--max-range` | `2000` | Initial plot half-extent (mm) |
| `--voxel-mm` | `40` | Accumulation voxel size (mm) |
| `--alpha` | `0.95` | Complementary-filter gyro weight (0..1) |
| `--mount-deg` | `0,0,0` | Fixed ToF→IMU mounting rotation `rx,ry,rz` (deg) |

### Limitations & calibration

These are inherent to the available sensors, not bugs:

- **Rotation-only.** There is no position tracking (accelerometer
  double-integration drifts uselessly), so this is a *pan/tilt-in-place*
  scanner, not SLAM. Accumulation assumes the sensor rotates about a roughly
  fixed point.
- **Yaw drifts.** With no magnetometer, integrated yaw slowly wanders. Press `r`
  to re-zero when it does.
- **Mounting alignment.** Fusion assumes the ToF and IMU are **rigidly mounted
  with aligned axes** (x=right, y=up, z=forward). With the ToF on flying leads
  and the IMU on the perfboard, accumulation is only meaningful once the two are
  fixed together. If the cloud tilts the wrong way under motion, correct the
  fixed offset with `--mount-deg`.

### Serial vs. BLE for the point cloud

A full 8×8 snapshot (~680 B) far exceeds the default BLE notify payload (~20 B),
so a connected BLE central receives only fragments unless MTU is negotiated.
**Use serial for the point cloud.** BLE works well for `sensor_listen.py`
spot-checks and for the smaller car-control command traffic.

## Installation

All tools share one requirements file:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r tools/requirements.txt
```

This pulls `pyserial` and `bleak` (transports) plus `numpy` and `matplotlib`
(point-cloud math and rendering).
