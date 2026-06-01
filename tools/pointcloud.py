"""Live 3D point-cloud visualization of the LEGO 42212 VL53L8CX ToF sensor,
with IMU-based orientation tracking and accumulation over time.

Each snapshot carries an 8x8 grid of distances (mm) plus the MPU accel/gyro.
We:
  1. Project the 64 ToF zones through their FoV angles into sensor-frame points.
  2. Estimate the rig's orientation from the IMU with a complementary filter
     (accelerometer fixes absolute roll/pitch via gravity; gyro tracks fast
     motion and integrates yaw).
  3. Rotate each frame into a gravity-aligned world frame and accumulate the
     points into a voxel grid, so panning the sensor builds up a denser cloud.

This is rotation-only fusion: the sensor is assumed to stay in roughly one
position and pan/tilt. There's no position tracking (accelerometer double-
integration drifts hopelessly), and yaw drifts slowly with no magnetometer.

IMPORTANT mounting assumption: the ToF and IMU are taken to be rigidly mounted
with aligned axes (x=right, y=up, z=forward). If your physical mounting differs,
the accumulated cloud will tilt the wrong way under motion -- correct it with
--mount-deg "rx,ry,rz" (a fixed rotation applied to ToF points before the IMU
orientation). With the ToF on flying leads (not fixed to the IMU), accumulation
is only meaningful once the two are taped together.

Reading reuses the same serial/BLE transports as sensor_listen.py.
"""

import argparse
import asyncio
import math
import re
import sys
import threading

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

try:
    import serial
    from serial import SerialException
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

try:
    import bleak
    BLEAK_AVAILABLE = True
except ImportError:
    BLEAK_AVAILABLE = False


# --- Sensor geometry -------------------------------------------------------

GRID = 8                      # 8x8 resolution (64 zones)
FOV_DEG = 45.0                # VL53L8CX square field of view (per axis)
INVALID_MAX_MM = 4000         # clamp / ignore readings beyond this

# Zone-center angle (radians) for each row/col across the FoV.
# Zone i center = -FoV/2 + (i + 0.5) * FoV/GRID
_HALF = math.radians(FOV_DEG) / 2.0
_STEP = math.radians(FOV_DEG) / GRID
ZONE_ANGLES = [-_HALF + (i + 0.5) * _STEP for i in range(GRID)]


def project_grid(distances_mm):
    """Project the 64 zone distances into Nx3 points (x, y, z) in mm.

    Convention: x = right, y = up, z = forward (out of the sensor).
    col -> azimuth (horizontal), row -> elevation (vertical), row 0 at top.
    Zeros / out-of-range readings are dropped.
    """
    points = []
    for row in range(GRID):
        for col in range(GRID):
            d = distances_mm[row * GRID + col]
            if d <= 0 or d > INVALID_MAX_MM:
                continue
            az = ZONE_ANGLES[col]
            el = ZONE_ANGLES[GRID - 1 - row]  # row 0 = top = +elevation
            x = d * math.sin(az) * math.cos(el)
            y = d * math.sin(el)
            z = d * math.cos(az) * math.cos(el)
            points.append((x, y, z))
    return np.array(points, dtype=float) if points else np.empty((0, 3))


def rotation_xyz(rx, ry, rz):
    """Rotation matrix Rz @ Ry @ Rx, angles in radians."""
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    rot_x = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    rot_y = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rot_z = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return rot_z @ rot_y @ rot_x


# --- Orientation tracking --------------------------------------------------

class OrientationTracker:
    """Complementary filter fusing accelerometer (absolute roll/pitch) and
    gyroscope (fast motion + integrated yaw) into roll/pitch/yaw (radians).

    Uses the standard z-up IMU convention for the gravity math. Yaw has no
    absolute reference (no magnetometer) so it drifts.
    """

    def __init__(self, alpha=0.95):
        self.alpha = alpha           # weight on gyro vs accel for roll/pitch
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.last_ts = None

    def reset(self):
        self.__init__(self.alpha)

    def update(self, accel, gyro, ts_ms):
        ax, ay, az = accel
        gx, gy, gz = gyro
        roll_acc = math.atan2(ay, az)
        pitch_acc = math.atan2(-ax, math.hypot(ay, az))

        if self.last_ts is None:
            self.roll, self.pitch, self.yaw = roll_acc, pitch_acc, 0.0
            self.last_ts = ts_ms
            return

        dt = (ts_ms - self.last_ts) / 1000.0
        self.last_ts = ts_ms
        if dt <= 0 or dt > 1.0:
            # Stalled stream or wrapped timestamp: trust accel, hold yaw.
            self.roll, self.pitch = roll_acc, pitch_acc
            return

        gxr, gyr, gzr = map(math.radians, (gx, gy, gz))
        roll_g = self.roll + gxr * dt
        pitch_g = self.pitch + gyr * dt
        self.yaw += gzr * dt
        self.roll = self.alpha * roll_g + (1 - self.alpha) * roll_acc
        self.pitch = self.alpha * pitch_g + (1 - self.alpha) * pitch_acc

    def matrix(self):
        """World-from-body rotation."""
        return rotation_xyz(self.roll, self.pitch, self.yaw)

    def degrees(self):
        return (math.degrees(self.roll), math.degrees(self.pitch),
                math.degrees(self.yaw))


# --- Accumulator -----------------------------------------------------------

class VoxelCloud:
    """Accumulates world-frame points into a voxel grid (dedup + bound)."""

    def __init__(self, voxel_mm=40.0, max_voxels=200000):
        self.voxel = voxel_mm
        self.max_voxels = max_voxels
        self.cells = {}              # (ix, iy, iz) -> (x, y, z)

    def add(self, world_pts):
        if not len(world_pts):
            return
        keys = np.floor(world_pts / self.voxel).astype(int)
        for key, pt in zip(map(tuple, keys), world_pts):
            if key not in self.cells:
                if len(self.cells) >= self.max_voxels:
                    return
                self.cells[key] = pt

    def points(self):
        if not self.cells:
            return np.empty((0, 3))
        return np.array(list(self.cells.values()))

    def clear(self):
        self.cells.clear()


# --- Snapshot parser -------------------------------------------------------

_KV_RE = re.compile(r"(a[xyz]|g[xyz])=\s*([+-]?[\d.]+)")


class SnapshotParser:
    """Parses the snapshot stream into complete frames bundling the timestamp,
    IMU accel/gyro, and the 8x8 ToF grid.

    Works on arbitrarily chunked input (BLE notifications are not line-aligned),
    so it buffers and only processes complete lines. Each finished snapshot
    bumps `frame_id` so consumers can detect new data.
    """

    def __init__(self):
        self._buf = ""
        self._collecting = False
        self._rows = []
        self._cur = {}               # accumulates fields for the in-progress snapshot
        self.frame = None            # last complete frame dict
        self.frame_id = 0

    def feed(self, text):
        self._buf += text
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            self._process_line(line)

    def _process_line(self, line):
        if "Sensors @" in line:
            m = re.search(r"@\s*(\d+)ms", line)
            self._cur = {"ts": int(m.group(1)) if m else None}
            self._collecting = False
            return

        kv = dict(_KV_RE.findall(line))
        if {"ax", "ay", "az"} <= kv.keys():
            self._cur["accel"] = (float(kv["ax"]), float(kv["ay"]), float(kv["az"]))
            return
        if {"gx", "gy", "gz"} <= kv.keys():
            self._cur["gyro"] = (float(kv["gx"]), float(kv["gy"]), float(kv["gz"]))
            return

        if "ToF (mm" in line:
            self._collecting = True
            self._rows = []
            return
        if self._collecting:
            nums = [int(n) for n in re.findall(r"-?\d+", line)]
            if len(nums) == GRID:
                self._rows.append(nums)
                if len(self._rows) == GRID:
                    self._cur["grid"] = [v for r in self._rows for v in r]
                    self._finish()
                    self._collecting = False
            else:
                self._collecting = False

    def _finish(self):
        self.frame = {
            "ts": self._cur.get("ts"),
            "accel": self._cur.get("accel", (0.0, 0.0, 1.0)),
            "gyro": self._cur.get("gyro", (0.0, 0.0, 0.0)),
            "grid": self._cur.get("grid"),
        }
        self.frame_id += 1


# --- Background reader -----------------------------------------------------

class SensorReader:
    """Reads the sensor stream on a background thread, parsing snapshots."""

    def __init__(self):
        self.parser = SnapshotParser()
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = None

    def latest(self):
        with self._lock:
            return self.parser.frame, self.parser.frame_id

    def _feed(self, text):
        with self._lock:
            self.parser.feed(text)

    def start_serial(self, port, baud):
        self._thread = threading.Thread(
            target=self._serial_loop, args=(port, baud), daemon=True)
        self._thread.start()

    def start_ble(self):
        self._thread = threading.Thread(target=self._ble_thread, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _serial_loop(self, port, baud):
        try:
            ser = serial.Serial(port, baud, timeout=0.2)
        except SerialException as error:
            print(f"Serial error: could not open {port}: {error}")
            return
        try:
            while not self._stop.is_set():
                data = ser.readline()
                if data:
                    self._feed(data.decode("utf-8", errors="replace"))
        finally:
            ser.close()

    def _ble_thread(self):
        try:
            asyncio.run(self._ble_loop())
        except Exception as error:
            print(f"BLE error: {error}")

    async def _ble_loop(self):
        TX_CHAR_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
        print("Scanning for LEGO-42212...")
        devices = await bleak.BleakScanner.discover()
        target = next((d for d in devices if d.name and "LEGO-42212" in d.name), None)
        if not target:
            print("LEGO-42212 not found.")
            self._stop.set()
            return
        print(f"Found LEGO-42212 at {target.address}")

        def on_notify(_char, data):
            self._feed(bytes(data).decode("utf-8", errors="replace"))

        async with bleak.BleakClient(target.address) as client:
            print("Connected. Streaming...")
            await client.start_notify(TX_CHAR_UUID, on_notify)
            while not self._stop.is_set() and client.is_connected:
                await asyncio.sleep(0.1)
            try:
                await client.stop_notify(TX_CHAR_UUID)
            except Exception:
                pass


# --- Visualization ---------------------------------------------------------

def run_visualization(reader, args):
    tracker = OrientationTracker(alpha=args.alpha)
    cloud = VoxelCloud(voxel_mm=args.voxel_mm)
    mount = rotation_xyz(*[math.radians(float(a)) for a in args.mount_deg.split(",")])

    state = {"last_id": -1, "accumulate": True, "paused": False, "limit": args.max_range}

    fig = plt.figure(figsize=(9, 7.5))
    ax = fig.add_subplot(111, projection="3d")

    def on_key(event):
        if event.key == "r":
            cloud.clear()
            tracker.reset()
        elif event.key == "a":
            state["accumulate"] = not state["accumulate"]
        elif event.key == " ":
            state["paused"] = not state["paused"]
    fig.canvas.mpl_connect("key_press_event", on_key)

    def update(_frame):
        frame, fid = reader.latest()
        is_new = fid != state["last_id"]
        state["last_id"] = fid

        if frame and frame.get("grid") and is_new and not state["paused"]:
            tracker.update(frame["accel"], frame["gyro"], frame["ts"])
            sensor_pts = project_grid(frame["grid"])
            if len(sensor_pts):
                # world = R_world_from_body @ R_mount @ tof_points
                world_pts = sensor_pts @ (tracker.matrix() @ mount).T
                if state["accumulate"]:
                    cloud.add(world_pts)
                update._current = world_pts

        ax.clear()
        accum = cloud.points()
        # Keep limits stable but grow to fit the accumulated extent.
        if len(accum):
            state["limit"] = max(state["limit"], float(np.abs(accum).max()))
        lim = state["limit"]
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.set_zlim(-lim, lim)
        ax.set_xlabel("X (mm)")
        ax.set_ylabel("Y up (mm)")
        ax.set_zlabel("Z (mm)")

        ax.scatter([0], [0], [0], c="red", marker="^", s=60)  # sensor origin

        if len(accum):
            sc = ax.scatter(accum[:, 0], accum[:, 1], accum[:, 2],
                            c=accum[:, 1], cmap="viridis",
                            vmin=-lim, vmax=lim, s=6, alpha=0.5)
            if not hasattr(update, "_cbar"):
                update._cbar = fig.colorbar(sc, ax=ax, shrink=0.6, label="height Y (mm)")

        current = getattr(update, "_current", None)
        if current is not None and len(current):
            ax.scatter(current[:, 0], current[:, 1], current[:, 2],
                       c="orange", s=22, depthshade=False)

        roll, pitch, yaw = tracker.degrees()
        ax.set_title("VL53L8CX + IMU point cloud")
        ax.text2D(0.02, 0.98,
                  f"roll={roll:+6.1f}  pitch={pitch:+6.1f}  yaw={yaw:+6.1f} deg\n"
                  f"voxels={len(accum)}   "
                  f"accumulate={'ON' if state['accumulate'] else 'off'}   "
                  f"{'PAUSED' if state['paused'] else ''}\n"
                  f"[r]eset  [a]ccumulate  [space]pause",
                  transform=ax.transAxes, fontsize=8, va="top", family="monospace")
        return []

    anim = FuncAnimation(fig, update, interval=80, cache_frame_data=False)
    fig._anim = anim  # keep a reference so it isn't garbage-collected
    try:
        plt.show()
    finally:
        reader.stop()


def main():
    parser = argparse.ArgumentParser(
        description="Live IMU-fused, time-accumulated point cloud of the LEGO 42212 ToF sensor")
    parser.add_argument("--mode", choices=["serial", "ble"], default="serial",
                        help="Read mode: 'serial' for USB, 'ble' for Bluetooth")
    parser.add_argument("--port", help="Serial port (serial mode), e.g., COM4")
    parser.add_argument("--baud", type=int, default=115200, help="Baud (default 115200)")
    parser.add_argument("--max-range", type=float, default=2000.0,
                        help="Initial plot half-extent in mm (default 2000)")
    parser.add_argument("--voxel-mm", type=float, default=40.0,
                        help="Voxel size for accumulation in mm (default 40)")
    parser.add_argument("--alpha", type=float, default=0.95,
                        help="Complementary-filter gyro weight 0..1 (default 0.95)")
    parser.add_argument("--mount-deg", default="0,0,0",
                        help="Fixed ToF->IMU mounting rotation 'rx,ry,rz' in degrees")
    args = parser.parse_args()

    reader = SensorReader()
    if args.mode == "serial":
        if not SERIAL_AVAILABLE:
            print("Error: pyserial required for serial mode (pip install pyserial)")
            return 1
        if not args.port:
            print("Error: --port required for serial mode (e.g., --port COM4)")
            return 1
        reader.start_serial(args.port, args.baud)
    else:
        if not BLEAK_AVAILABLE:
            print("Error: bleak required for BLE mode (pip install bleak)")
            return 1
        reader.start_ble()

    print("Opening point-cloud window. Keys: [r]eset  [a]ccumulate  [space]pause. Close to stop.")
    run_visualization(reader, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
