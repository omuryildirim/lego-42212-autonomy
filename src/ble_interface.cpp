#include "ble_interface.h"
#include "config.h"

#if ENABLE_BLE_INTERFACE

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// Forward declaration - implemented in main.cpp
void processCommand(char* line);

namespace BLEInterface {

static BLEServer* bleServer = nullptr;
static BLECharacteristic* rxCharacteristic = nullptr;
static BLECharacteristic* txCharacteristic = nullptr;
static bool bleConnected = false;
static std::string lastCommand;
static char pendingCommand[96] = {0};
static bool commandPending = false;

class ServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer* pServer, esp_ble_gatts_cb_param_t* param) override {
    bleConnected = true;
    Serial.println("BLE client connected");
  }

  void onDisconnect(BLEServer* pServer, esp_ble_gatts_cb_param_t* param) override {
    bleConnected = false;
    Serial.println("BLE client disconnected");
    pServer->startAdvertising();
  }
};

class RxCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic* pCharacteristic) override {
    std::string rxValue = pCharacteristic->getValue();

    if (rxValue.length() > 0 && rxValue.length() < 96) {
      // Just store the command - don't process in interrupt context
      strcpy(pendingCommand, rxValue.c_str());
      // Remove newline if present
      size_t len = strlen(pendingCommand);
      if (len > 0 && pendingCommand[len - 1] == '\n') {
        pendingCommand[len - 1] = '\0';
      }
      commandPending = true;
    }
  }
};

void setup() {
  BLEDevice::init(BLE_DEVICE_NAME);
  Serial.println("BLE device initialized");
  
  bleServer = BLEDevice::createServer();
  bleServer->setCallbacks(new ServerCallbacks());

  BLEService* bleService = bleServer->createService(BLE_SERVICE_UUID);
  Serial.println("BLE service created");

  rxCharacteristic = bleService->createCharacteristic(
    BLE_RX_CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR
  );
  rxCharacteristic->setCallbacks(new RxCallbacks());
  Serial.println("BLE RX characteristic ready (write commands here)");

  txCharacteristic = bleService->createCharacteristic(
    BLE_TX_CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
  );
  txCharacteristic->addDescriptor(new BLE2902());
  Serial.println("BLE TX characteristic ready (receive status here)");

  bleService->start();

  BLEAdvertising* pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(BLE_SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);
  pAdvertising->setMinPreferred(0x12);
  BLEDevice::startAdvertising();

  Serial.printf("BLE advertising as '%s'...\n", BLE_DEVICE_NAME);
}

void update() {
  // Process BLE commands that were received in interrupt context
  if (commandPending) {
    commandPending = false;
    Serial.printf("BLE received: %s\n", pendingCommand);
    processCommand(pendingCommand);
  }
}

bool isConnected() {
  return bleConnected;
}

void sendStatus(const char* message) {
  if (bleConnected && txCharacteristic != nullptr) {
    txCharacteristic->setValue((uint8_t*)message, strlen(message));
    txCharacteristic->notify();
  }
}

}  // namespace BLEInterface

#else

namespace BLEInterface {

void setup() {
  // BLE disabled
}

void update() {
  // BLE disabled
}

bool isConnected() {
  return false;
}

void sendStatus(const char* message) {
  // BLE disabled
}

}  // namespace BLEInterface

#endif  // ENABLE_BLE_INTERFACE
