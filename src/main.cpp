#include <Arduino.h>
#include <Wire.h>
#include <vl53l8cx_class.h>
#include "config.h"
#include "ble_interface.h"

namespace {

// Motor pins from the perfboard. Held inert in sensor bench mode so the DRV8833
// outputs stay high-impedance even if the buck is powered.
constexpr int kMotorIn1Pin = 3;
constexpr int kMotorIn2Pin = 4;

// I2C shared by MPU-9265 (on perfboard, row N) and SATEL-VL53L8 (off-board).
constexpr int kI2cSdaPin = 6;
constexpr int kI2cSclPin = 7;
// 100 kHz, not 400 kHz: the ToF's ~80 KB firmware-blob upload in init_sensor()
// is marginal at 400 kHz over the SATEL's flying-lead wiring. The IMU's tiny
// single-register reads tolerate 400 kHz, but the bulk upload does not.
constexpr uint32_t kI2cClockHz = 100000;

// VL53L8CX low-power enable. HIGH = chip awake and on the I2C bus.
constexpr int kTofLpnPin = 10;

constexpr uint8_t kMpuI2cAddr = 0x68;
constexpr uint8_t kMpuRegPwrMgmt1 = 0x6B;
constexpr uint8_t kMpuRegWhoAmI = 0x75;
constexpr uint8_t kMpuRegAccelXoutH = 0x3B;

// Default ranges after wake: ±2 g, ±250 dps. See MPU-9250 register map §4.5.
constexpr float kAccelLsbPerG = 16384.0f;
constexpr float kGyroLsbPerDps = 131.0f;

// 10 Hz: matches the ToF 10 Hz ranging and gives the host enough IMU samples
// for usable gyro integration / orientation tracking. A full 8x8 snapshot is
// ~680 B, so 10 Hz (~6.8 KB/s) fits comfortably in 115200 baud (~11.5 KB/s).
constexpr uint32_t kSensorPeriodMs = 100;

// ToF grid edge: 8 -> 8x8 (64 zones). Max ranging frequency is 15 Hz at 8x8.
constexpr int kTofGrid = 8;

VL53L8CX tof(&Wire, kTofLpnPin);
bool mpuReady = false;
bool tofReady = false;
// Captured by setupTof() so the failure is visible in the snapshot stream even
// when the boot log was missed (native USB-CDC can't be reset via RTS).
const char* tofFailStep = "none";
uint8_t tofFailStatus = 0;
uint32_t lastSensorTickMs = 0;
// Large enough for the 8x8 grid (64 zones ~430 chars) plus IMU + framing.
char snapshotBuf[1024];

bool mpuReadRegs(uint8_t reg, uint8_t* buf, size_t len) {
  Wire.beginTransmission(kMpuI2cAddr);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) {
    return false;
  }
  const size_t received = Wire.requestFrom(static_cast<uint8_t>(kMpuI2cAddr), static_cast<uint8_t>(len));
  if (received != len) {
    return false;
  }
  for (size_t i = 0; i < len; ++i) {
    buf[i] = Wire.read();
  }
  return true;
}

bool mpuWriteReg(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(kMpuI2cAddr);
  Wire.write(reg);
  Wire.write(value);
  return Wire.endTransmission() == 0;
}

bool setupMpu() {
  uint8_t whoami = 0;
  if (!mpuReadRegs(kMpuRegWhoAmI, &whoami, 1)) {
    Serial.println("MPU: WHO_AM_I read failed");
    return false;
  }
  Serial.printf("MPU WHO_AM_I=0x%02X\n", whoami);
  if (whoami == 0x00 || whoami == 0xFF) {
    return false;
  }
  if (!mpuWriteReg(kMpuRegPwrMgmt1, 0x00)) {
    Serial.println("MPU: wake failed");
    return false;
  }
  delay(50);
  return true;
}

bool setupTof() {
  pinMode(kTofLpnPin, OUTPUT);
  digitalWrite(kTofLpnPin, HIGH);
  delay(10);

  uint8_t status = tof.begin();
  if (status != 0) {
    tofFailStep = "begin";
    tofFailStatus = status;
    Serial.printf("ToF: begin() failed (status=%u)\n", status);
    return false;
  }
  // init_sensor() uploads the ~80 KB firmware blob; takes a few seconds.
  status = tof.init_sensor();
  if (status != 0) {
    tofFailStep = "init_sensor";
    tofFailStatus = status;
    Serial.printf("ToF: init_sensor() failed (status=%u)\n", status);
    return false;
  }
  status = tof.vl53l8cx_set_resolution(VL53L8CX_RESOLUTION_8X8);
  if (status != 0) {
    tofFailStep = "set_resolution";
    tofFailStatus = status;
    Serial.printf("ToF: set_resolution failed (status=%u)\n", status);
    return false;
  }
  status = tof.vl53l8cx_set_ranging_frequency_hz(10);
  if (status != 0) {
    tofFailStep = "set_freq";
    tofFailStatus = status;
    Serial.printf("ToF: set_ranging_frequency_hz failed (status=%u)\n", status);
    return false;
  }
  status = tof.vl53l8cx_start_ranging();
  if (status != 0) {
    tofFailStep = "start_ranging";
    tofFailStatus = status;
    Serial.printf("ToF: start_ranging failed (status=%u)\n", status);
    return false;
  }
  return true;
}

void initMotorPinsInert() {
  pinMode(kMotorIn1Pin, OUTPUT);
  pinMode(kMotorIn2Pin, OUTPUT);
  digitalWrite(kMotorIn1Pin, LOW);
  digitalWrite(kMotorIn2Pin, LOW);
}

size_t appendImuSection(char* buf, size_t cap) {
  if (!mpuReady) {
    return snprintf(buf, cap, "IMU  offline\n");
  }

  uint8_t raw[14] = {0};
  if (!mpuReadRegs(kMpuRegAccelXoutH, raw, sizeof(raw))) {
    return snprintf(buf, cap, "IMU  read failed\n");
  }

  const int16_t ax = static_cast<int16_t>((raw[0] << 8) | raw[1]);
  const int16_t ay = static_cast<int16_t>((raw[2] << 8) | raw[3]);
  const int16_t az = static_cast<int16_t>((raw[4] << 8) | raw[5]);
  const int16_t tempRaw = static_cast<int16_t>((raw[6] << 8) | raw[7]);
  const int16_t gx = static_cast<int16_t>((raw[8] << 8) | raw[9]);
  const int16_t gy = static_cast<int16_t>((raw[10] << 8) | raw[11]);
  const int16_t gz = static_cast<int16_t>((raw[12] << 8) | raw[13]);
  const float tempC = tempRaw / 333.87f + 21.0f;

  return snprintf(buf, cap,
                  "IMU  ax=%+6.3f ay=%+6.3f az=%+6.3f g\n"
                  "     gx=%+7.2f gy=%+7.2f gz=%+7.2f dps   T=%.1fC\n",
                  ax / kAccelLsbPerG, ay / kAccelLsbPerG, az / kAccelLsbPerG,
                  gx / kGyroLsbPerDps, gy / kGyroLsbPerDps, gz / kGyroLsbPerDps,
                  tempC);
}

size_t appendTofSection(char* buf, size_t cap) {
  if (!tofReady) {
    // Live-probe the ToF's 7-bit address (0x29) to tell a dead/unpowered chip
    // (NACK) apart from a chip that ACKs but fails firmware init.
    Wire.beginTransmission(0x29);
    const bool tofAcks = (Wire.endTransmission() == 0);
    return snprintf(buf, cap,
                    "ToF  offline (failed at %s, status=%u, 0x29 %s)\n",
                    tofFailStep, tofFailStatus, tofAcks ? "ACK" : "NACK");
  }

  uint8_t isReady = 0;
  if (tof.vl53l8cx_check_data_ready(&isReady) != 0 || !isReady) {
    return snprintf(buf, cap, "ToF  no new frame\n");
  }

  VL53L8CX_ResultsData results;
  if (tof.vl53l8cx_get_ranging_data(&results) != 0) {
    return snprintf(buf, cap, "ToF  read failed\n");
  }

  size_t pos = snprintf(buf, cap, "ToF (mm, %dx%d):\n", kTofGrid, kTofGrid);
  for (int row = 0; row < kTofGrid && pos < cap; ++row) {
    pos += snprintf(buf + pos, cap - pos, "    ");
    for (int col = 0; col < kTofGrid && pos < cap; ++col) {
      const int idx = row * kTofGrid + col;
      pos += snprintf(buf + pos, cap - pos, " %5d", results.distance_mm[idx]);
    }
    pos += snprintf(buf + pos, cap - pos, "\n");
  }
  return pos;
}

void emitSnapshot() {
  size_t pos = snprintf(snapshotBuf, sizeof(snapshotBuf),
                        "==================== Sensors @ %lums ====================\n",
                        static_cast<unsigned long>(millis()));
  pos += appendImuSection(snapshotBuf + pos, sizeof(snapshotBuf) - pos);
  pos += appendTofSection(snapshotBuf + pos, sizeof(snapshotBuf) - pos);
  pos += snprintf(snapshotBuf + pos, sizeof(snapshotBuf) - pos,
                  "============================================================\n");

  Serial.print(snapshotBuf);
  BLEInterface::sendStatus(snapshotBuf);
}

}  // namespace

// Required by ble_interface.cpp / serial_interface.cpp. Sensor bench mode
// ignores commands — the BLE TX is a one-way data stream.
void processCommand(char* line) {
  Serial.printf("Command ignored in sensor bench mode: %s\n", line);
}

void printHelp() {
  Serial.println("Sensor bench mode — no commands accepted.");
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("LEGO 42212 sensor bench");

  initMotorPinsInert();

  Wire.begin(kI2cSdaPin, kI2cSclPin);
  Wire.setClock(kI2cClockHz);

  mpuReady = setupMpu();
  Serial.printf("MPU ready: %s\n", mpuReady ? "yes" : "no");

  tofReady = setupTof();
  Serial.printf("ToF ready: %s\n", tofReady ? "yes" : "no");

#if ENABLE_BLE_INTERFACE
  Serial.println("Initializing BLE interface...");
  BLEInterface::setup();
#endif

  Serial.println("Streaming sensor snapshots");
}

void loop() {
#if ENABLE_BLE_INTERFACE
  BLEInterface::update();
#endif

  if (millis() - lastSensorTickMs >= kSensorPeriodMs) {
    lastSensorTickMs = millis();
    emitSnapshot();
  }

  delay(10);
}
