# Motor mechanical integration

How the two motors tie into the LEGO 42212 chassis: the GA12-N20 drive motor at the rear, and the SG90 steering servo at the front. Adapter and bracket part details live in [3d-printing/](3d-printing/README.md); this doc covers the surrounding integration and the mechanical compliance that affects control.

## Drive motor (N20)

The N20's rotation reaches the rear wheels through three stages, each adding some compliance worth being aware of when interpreting motor-side encoder data.

### Chain

1. **N20 D-shaft** drives the [3D-printed coupler](3d-printing/ga12-n20/README.md), which presents a LEGO Technic axle on its output side.
2. A **knob gear** on that axle meshes with a second knob gear on a perpendicular axle — the 90° change of direction.
3. The perpendicular axle carries a **small gear at each outer end**, each meshing with a **larger gear on a wheel shaft**. The size mismatch is a speed reduction: wheels turn slower than the perpendicular axle with proportionally more torque.

![Drive chain](images/drivetrain.jpg)
*Image coming soon: N20 → coupler → knob gears → perpendicular axle → wheel-axle gears.*

## Steering servo (SG90)

TBD — to document: servo mounting location in the chassis, the [3D-printed adapter](3d-printing/sg90/README.md) from servo horn to LEGO Technic axle, the linkage to the steering arm, and the asymmetry / compliance sources that motivate the firmware trim.

Firmware-side calibration (`kServoSide`, `kSteeringTrim`) is documented in [steering-calibration.md](steering-calibration.md).
