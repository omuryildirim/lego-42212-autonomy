#pragma once

// Build-time operating mode. Exactly one translation unit (car_control.cpp or
// sensor_bench.cpp, selected by ENABLE_SENSOR_MODE in config.h) implements
// these plus the global processCommand()/printHelp() used by the interfaces.
namespace Mode {

// Mode-specific hardware bring-up, called once from setup() after Serial is up.
void setup();

// Mode-specific work, called every loop() iteration after the interfaces are
// serviced. Owns its own pacing delay.
void loop();

}  // namespace Mode
