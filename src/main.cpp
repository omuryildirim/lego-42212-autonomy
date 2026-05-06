#include <Arduino.h>
#include <ESP32Servo.h>
#include "config.h"
#include "serial_interface.h"
#include "ble_interface.h"

namespace {

constexpr int kMotorIn1Pin = 4;
constexpr int kMotorIn2Pin = 5;
constexpr int kServoPin = 6;

constexpr int kMotorPwmChannelA = 0;
constexpr int kMotorPwmChannelB = 1;
constexpr int kMotorPwmFrequencyHz = 20000;
constexpr int kMotorPwmResolutionBits = 8;
constexpr int kMotorPwmMaxDuty = (1 << kMotorPwmResolutionBits) - 1;

constexpr int kServoMinPulseUs = 500;
constexpr int kServoMaxPulseUs = 2400;
constexpr int kSteeringCenterDeg = 90;
constexpr int kSteeringMaxOffsetDeg = 35;
// Mechanical trim added to every steering input so the linkage rests centered.
constexpr float kSteeringTrim = 0.2f;
// Servo mount orientation: +1 if the label faces up, -1 if it faces down. The
// -1 case mirrors steering left/right to match the driver's perspective.
constexpr int kServoSide = -1;

constexpr float kThrottleDeadzone = 0.10f;
constexpr float kSteeringDeadzone = 0.08f;
constexpr uint32_t kCommandTimeoutMs = 500;

Servo steeringServo;
float currentThrottle = 0.0f;
float currentSteering = 0.0f;
uint32_t lastCommandMs = 0;
char commandBuffer[96];
size_t commandLength = 0;

float clampUnit(float value) {
  if (value > 1.0f) {
    return 1.0f;
  }
  if (value < -1.0f) {
    return -1.0f;
  }
  return value;
}

float applyDeadzone(float value, float deadzone) {
  if (fabsf(value) < deadzone) {
    return 0.0f;
  }

  const float magnitude = (fabsf(value) - deadzone) / (1.0f - deadzone);
  return copysignf(magnitude, value);
}

void setMotorThrottle(float throttle) {
  const float clipped = applyDeadzone(clampUnit(throttle), kThrottleDeadzone);
  const int duty = static_cast<int>(fabsf(clipped) * kMotorPwmMaxDuty);

  if (duty == 0) {
    ledcDetachPin(kMotorIn1Pin);
    ledcDetachPin(kMotorIn2Pin);
    pinMode(kMotorIn1Pin, OUTPUT);
    pinMode(kMotorIn2Pin, OUTPUT);
    digitalWrite(kMotorIn1Pin, HIGH);
    digitalWrite(kMotorIn2Pin, HIGH);
    return;
  }

  if (duty >= kMotorPwmMaxDuty) {
    ledcDetachPin(kMotorIn1Pin);
    ledcDetachPin(kMotorIn2Pin);
    pinMode(kMotorIn1Pin, OUTPUT);
    pinMode(kMotorIn2Pin, OUTPUT);
    digitalWrite(kMotorIn1Pin, clipped > 0.0f ? HIGH : LOW);
    digitalWrite(kMotorIn2Pin, clipped > 0.0f ? LOW : HIGH);
    return;
  }

  if (clipped > 0.0f) {
    ledcAttachPin(kMotorIn1Pin, kMotorPwmChannelA);
    ledcDetachPin(kMotorIn2Pin);
    pinMode(kMotorIn2Pin, OUTPUT);
    ledcWrite(kMotorPwmChannelA, duty);
    digitalWrite(kMotorIn2Pin, LOW);
    return;
  }

  if (clipped < 0.0f) {
    ledcDetachPin(kMotorIn1Pin);
    pinMode(kMotorIn1Pin, OUTPUT);
    digitalWrite(kMotorIn1Pin, LOW);
    ledcAttachPin(kMotorIn2Pin, kMotorPwmChannelB);
    ledcWrite(kMotorPwmChannelB, duty);
    return;
  }

  ledcDetachPin(kMotorIn1Pin);
  ledcDetachPin(kMotorIn2Pin);
  pinMode(kMotorIn1Pin, OUTPUT);
  pinMode(kMotorIn2Pin, OUTPUT);
  digitalWrite(kMotorIn1Pin, HIGH);
  digitalWrite(kMotorIn2Pin, HIGH);
}

void setSteering(float steering) {
  const float clipped = applyDeadzone(clampUnit(steering), kSteeringDeadzone);
  const int targetAngle = kSteeringCenterDeg + static_cast<int>(kServoSide * (clipped + kSteeringTrim) * kSteeringMaxOffsetDeg);
  steeringServo.write(targetAngle);
}

void applyOutputs(float throttle, float steering) {
  currentThrottle = clampUnit(throttle);
  currentSteering = clampUnit(steering);
  setMotorThrottle(currentThrottle);
  setSteering(currentSteering);
}

void setNeutralOutputs() {
  applyOutputs(0.0f, 0.0f);
}

void printStatus(const char* source) {
  Serial.printf("%s throttle=%.2f steering=%.2f\n", source, currentThrottle, currentSteering);
}

void markCommandReceived() {
  lastCommandMs = millis();
}

}  // namespace

void printHelp() {
  Serial.println("Commands:");
  Serial.println("  drive <throttle -1..1> <steering -1..1>");
  Serial.println("  throttle <value -1..1>");
  Serial.println("  steering <value -1..1>");
  Serial.println("  stop");
  Serial.println("  help");
}

void processCommand(char* line) {
  float firstValue = 0.0f;
  float secondValue = 0.0f;

  if (sscanf(line, "drive %f %f", &firstValue, &secondValue) == 2) {
    applyOutputs(firstValue, secondValue);
    markCommandReceived();
    printStatus("drive");
    return;
  }

  if (sscanf(line, "throttle %f", &firstValue) == 1) {
    applyOutputs(firstValue, currentSteering);
    markCommandReceived();
    printStatus("throttle");
    return;
  }

  if (sscanf(line, "steering %f", &firstValue) == 1) {
    applyOutputs(currentThrottle, firstValue);
    markCommandReceived();
    printStatus("steering");
    return;
  }

  if (strcmp(line, "stop") == 0) {
    setNeutralOutputs();
    markCommandReceived();
    printStatus("stop");
    return;
  }

  if (strcmp(line, "help") == 0) {
    printHelp();
    return;
  }

  Serial.printf("Unknown command: %s\n", line);
  printHelp();
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Starting LEGO 42212 controller");

  ledcSetup(kMotorPwmChannelA, kMotorPwmFrequencyHz, kMotorPwmResolutionBits);
  ledcSetup(kMotorPwmChannelB, kMotorPwmFrequencyHz, kMotorPwmResolutionBits);
  ledcAttachPin(kMotorIn1Pin, kMotorPwmChannelA);
  ledcAttachPin(kMotorIn2Pin, kMotorPwmChannelB);

  steeringServo.setPeriodHertz(50);
  steeringServo.attach(kServoPin, kServoMinPulseUs, kServoMaxPulseUs);
  setNeutralOutputs();
  printHelp();

  // Initialize communication interfaces
#if ENABLE_SERIAL_INTERFACE
  Serial.println("Initializing Serial interface...");
  SerialInterface::setup();
#endif

#if ENABLE_BLE_INTERFACE
  Serial.println("Initializing BLE interface...");
  BLEInterface::setup();
#endif

  Serial.println("Ready for commands");
}

void loop() {
#if ENABLE_SERIAL_INTERFACE
  SerialInterface::update();
#endif

#if ENABLE_BLE_INTERFACE
  BLEInterface::update();
#endif

  if (lastCommandMs != 0 && millis() - lastCommandMs > kCommandTimeoutMs) {
    setNeutralOutputs();
    lastCommandMs = 0;
    printStatus("timeout");
  }

  delay(20);
}