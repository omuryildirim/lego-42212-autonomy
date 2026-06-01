#include <Arduino.h>
#include "config.h"
#include "mode.h"
#include "serial_interface.h"
#include "ble_interface.h"

// The operating mode (car control vs sensor bench) is selected at build time by
// ENABLE_SENSOR_MODE in config.h and implemented in car_control.cpp /
// sensor_bench.cpp. This file is mode-agnostic: it brings up the chosen mode and
// the serial/BLE interfaces, then services them each iteration.

void setup() {
  Serial.begin(115200);
  delay(1000);

  Mode::setup();

#if ENABLE_SERIAL_INTERFACE
  Serial.println("Initializing Serial interface...");
  SerialInterface::setup();
#endif

#if ENABLE_BLE_INTERFACE
  Serial.println("Initializing BLE interface...");
  BLEInterface::setup();
#endif

  Serial.println("Ready");
}

void loop() {
#if ENABLE_SERIAL_INTERFACE
  SerialInterface::update();
#endif

#if ENABLE_BLE_INTERFACE
  BLEInterface::update();
#endif

  Mode::loop();
}
