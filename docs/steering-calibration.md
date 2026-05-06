# Steering calibration

Once the [servo bench test](servo-breadboard-setup.md) works and the servo is connected to the steering linkage on the chassis, two constants in [../src/main.cpp](../src/main.cpp) align the firmware with your physical build. Edit, reflash, and retest after each change.

## `kServoSide`

Servo mount orientation. Set to `+1` when the servo's label faces up, `-1` when it faces down. The `-1` case mirrors left/right inside the firmware so steering matches the driver's perspective.

**Symptom:** pressing **A** turns the wheels right (and **D** turns them left). Flip the sign.

## `kSteeringTrim`

Fractional bias added to every steering input, scaled by the maximum steering angle. Range roughly `-1.0..1.0`. Compensates for asymmetry in the linkage so the wheels rest straight when the controller is at center.

**Symptom:** the wheels sit off-center when no key is pressed. Nudge `kSteeringTrim` in small steps, e.g. `0.05`, until they track straight. Positive values bias one way, negative the other — direction depends on linkage geometry, so try a small step and observe.

The trim is applied in the same space as the user input, so flipping `kServoSide` also flips the effective direction of the trim. After changing `kServoSide`, re-check the trim.
