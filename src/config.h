#pragma once

// Operating mode
//   0 = car control: drive the N20 motor + steering servo from serial/BLE
//       commands (the default).
//   1 = sensor bench: stream MPU-9265 + VL53L8CX snapshots; motor held inert.
#define ENABLE_SENSOR_MODE 0

// Communication interface selection
// Set to 1 to enable, 0 to disable. Both modes use serial and BLE.
#define ENABLE_SERIAL_INTERFACE 1
#define ENABLE_BLE_INTERFACE 1

// BLE Configuration
#define BLE_DEVICE_NAME "LEGO-42212"

// Standard UART-like BLE UUIDs
#define BLE_SERVICE_UUID "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
#define BLE_RX_CHARACTERISTIC_UUID "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
#define BLE_TX_CHARACTERISTIC_UUID "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
